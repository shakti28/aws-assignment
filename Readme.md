EC2 Instance Python Script
This Python script is run on an EC2 instance created by the Pulumi program in this repository. The script writes the numbers 1 to 100 to a file named output.txt in the /tmp directory of the instance.

Usage
To use this script, you must have an AWS account and have Pulumi installed. Then, follow these steps:

Clone this repository to your local machine.
Configure Pulumi to use your AWS credentials by running pulumi login aws.
Navigate to the aws-ec2-instance directory.
Run pulumi up to create the EC2 instance and associated resources.
Wait for the program to finish running. This may take a few minutes.
SSH into the EC2 instance by running ssh ec2-user@<public_ip_address>.
Navigate to the /tmp directory by running cd /tmp.
View the output.txt file by running cat output.txt.
When you are finished, run pulumi destroy to delete all of the resources that were created.
Script Details
Here is the code for the Python script:

python
Copy code
with open("/tmp/output.txt", "w") as f:
    for i in range(1, 101):
        f.write(str(i) + "\n")
        
The script first opens a file named output.txt in write mode using a with statement. The file is located in the /tmp directory of the instance. The script then uses a for loop to write the numbers 1 to 100 to the file, each on a separate line. Finally, the script closes the file.

This script is run as part of the user data passed to the EC2 instance when it is created. The user data is a Bash script that installs Python on the instance and then runs this Python script.