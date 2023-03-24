import pulumi
import pulumi_aws as aws

# Configure AWS provider
config = pulumi.Config()
aws_region = config.require('awsRegion')
aws_provider = aws.Provider('aws-provider', region=aws_region)

# Create a VPC
vpc = aws.ec2.Vpc('my-vpc', cidr_block='10.0.0.0/16')

# Create a private subnet in the VPC
private_subnet = aws.ec2.Subnet('my-private-subnet',
                                cidr_block='10.0.1.0/24',
                                vpc_id=vpc.id,
                                map_public_ip_on_launch=False)

# Create a security group for the EC2 instance
sg = aws.ec2.SecurityGroup('my-sg',
                           vpc_id=vpc.id,
                           description='Enable HTTP access',
                           ingress=[
                               aws.ec2.SecurityGroupIngressArgs(
                                   protocol='tcp',
                                   from_port=80,
                                   to_port=80,
                                   cidr_blocks=['0.0.0.0/0']
                               )
                           ])

# Create an EBS volume
ebs_volume = aws.ebs.Volume('my-ebs-volume', 
                            availability_zone=aws_region + 'a',
                            size=10,
                            tags={
                                'Name': 'my-ebs-volume'
                            })

# Create an EC2 instance
instance = aws.ec2.Instance('my-ec2-instance',
                            instance_type='t2.micro',
                            ami='ami-0c94855ba95c71c99',
                            subnet_id=private_subnet.id,
                            vpc_security_group_ids=[sg.id],
                            user_data=pulumi.Output.all(ebs_volume.id).apply(lambda args: f'''#!/bin/bash
                                echo "Creating mount point for EBS volume"
                                sudo mkdir /data
                                echo "Mounting EBS volume"
                                sudo mount /dev/xvdf /data
                                echo "Configuring permissions for ec2-user"
                                sudo chown ec2-user /data
                                echo "Writing Python script to /home/ec2-user"
                                echo "
                                with open('/data/output.txt', 'w') as f:
                                    for i in range(1, 101):
                                        f.write(str(i) + '\\n')
                                " > /home/ec2-user/script.py
                                echo "Running Python script"
                                python3 /home/ec2-user/script.py
                                echo "Script finished"
                            '''),
                            tags={
                                'Name': 'my-ec2-instance'
                            })

# Attach the EBS volume to the EC2 instance
ebs_attachment = aws.ec2.VolumeAttachment('my-ebs-attachment',
                                          volume_id=ebs_volume.id,
                                          instance_id=instance.id,
                                          device_name='/dev/xvdf')

# Create an S3 bucket
bucket = aws.s3.Bucket('my-s3-bucket',
                       acl='private')

# Add permissions to the EC2 instance to read and write objects in the S3 bucket
aws.s3.BucketPolicy('my-s3-bucket-policy',
                    bucket=bucket.id,
                    policy=pulumi.Output.all(instance.id, bucket.arn).apply(lambda args: f'''{{
                        "Version": "2012-10-17",
                        "Statement": [
                            {{
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetObject",
                                    "s3:PutObject"
                                ],
                                "Resource": "{args[1]}/*",
                                "Principal": {{
                                    "AWS": "{args[0]}"
                                }}
                            }}
                        ]
                    }}'''))
