import boto3 
import os 
import json
from requests import get
import time
import subprocess

ip = get('https://api.ipify.org').text
print('Your IP Address: ' + ip)
iam = boto3.client('iam')
client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

def clean():
    
    # client.delete_key_pair(KeyName=key_name)
    client.delete_security_group(GroupName='demo_group')
    iam.delete_group(GroupName="admin")
    iam.remove_role_from_instance_profile(RoleName='demo', InstanceProfileName="demo_profile")
    iam.delete_instance_profile(InstanceProfileName="demo_profile")
    iam.delete_role(RoleName="demo")

print("Creating group...")  
response = iam.create_group(
    Path ="/",
    GroupName="admin"
)
trust_policy={
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
print("Group created.")

print("Creating identity access management role...")
response = iam.create_role(
    RoleName='demo',
    AssumeRolePolicyDocument=json.dumps(trust_policy)    
)
print("Role created.")

# there is a race condition for when an instance profile is created have to wait a set period
# of time before you can create an instance with it
print("Creating instance profile...")
response = iam.create_instance_profile(
    InstanceProfileName="demoprofile"
)
instance_profile_arn = response['InstanceProfile']['Arn']
response = iam.add_role_to_instance_profile(
    InstanceProfileName="demoprofile",
    RoleName="demo"
)
print("(will take approximately 20 seconds)")
time.sleep(20)
print("Instance profile created.")

print("Creating security group for instance inbound traffic...")
response = client.create_security_group(
    Description='demo secutrity group for the coursework should allow all outside connections',
    GroupName='demo_group'
)
response = client.authorize_security_group_ingress(
    GroupName='demo_group',
    IpPermissions=[
        {
            'FromPort':22,
            'ToPort':22,
            'IpProtocol':'TCP',
            'IpRanges': [
                {
                    'CidrIp': ip + '/32',
                    'Description': 'Allow inbound SSH access to Linux instances from IPv4 IP addresses in your network (over the Internet gateway)'
                }
            ]
        },
        {
            'FromPort':22,
            'ToPort':22,
            'IpProtocol':'TCP',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0' + '/0',
                    'Description': 'Allow inbound SSH access to Linux instances from IPv4 IP addresses in your network (over the Internet gateway)'
                }
            ]
        }
        
    ]
)
# print("(will take approximately 30 seconds)")
# time.sleep(30)
print("Security group created.")

key_name = 'ec2-keypair'
print("Creating Key Pair " + key_name + "...")
outfile = open('ec2-keypair.pem', 'w')
key_pair = ec2.create_key_pair(KeyName=key_name)
key_pair_out = str(key_pair.key_material)
outfile.write(key_pair_out)
outfile.close()
os.system("chmod 400 ec2-keypair.pem")
print(key_name + " created and saved to local directory.")

instances = ec2.create_instances(
    ImageId = 'ami-00a1270ce1e007c27',
    MinCount = 1,
    MaxCount = 1,
    InstanceType = 't2.micro',
    KeyName = key_name,
    Monitoring = {
        'Enabled': True
    },
    IamInstanceProfile={
        # "Arn": instance_profile_arn,
        "Name":"demoprofile"
         
    },
    SecurityGroups=[
        'demo_group',
    ]
    
) 

count = 0
for instance in instances:
    print("Starting Instance " + str(count)+ "...")
    instance.wait_until_running()
    instance.load()
    ip_address = instance.public_ip_address.replace('.','-')
    print("Instance " + str(count) + " IP Address: " + instance.public_ip_address)
    os.system('scp -o "StrictHostKeyChecking no" -i %s %s ec2-user@ec2-%s.eu-west-2.compute.amazonaws.com:proof_of_work.py' % ('ec2-keypair.pem', 'proof_of_work.py', ip_address))
    instance.terminate()
    count += 1
    
# clean()