import boto3 
import os 
import json
from requests import get
import time

def cloud_setup():
    iam = boto3.client('iam')
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    ip = get('https://api.ipify.org').text
    print('Your IP Address: ' + ip)

    print("Starting setup...")
    print("Creating group...")  
    response = iam.create_group(
        Path ="/",
        GroupName="admin"
    )
    trust_policy={
    "Version": "2012-10-17",
    "Statement": [
            {
            "Sid": "1",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action":[
                    "sts:AssumeRole" 
                ] 
            }
        ]
    }
    iam.attach_group_policy(
        GroupName="admin",
        PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess"
    )
    print("Group created.")

    print("Creating identity access management role...")
    response = iam.create_role(
        RoleName='demo',
        AssumeRolePolicyDocument=json.dumps(trust_policy)    
    )
    response = iam.attach_role_policy(
        RoleName='demo',
        PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
    )
    response = iam.attach_role_policy(
        RoleName='demo',
        PolicyArn='arn:aws:iam::aws:policy/AmazonSSMFullAccess'
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
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Allow inbound SSH access to Linux instances from IPv4 IP addresses in your network (over the Internet gateway)'
                    }
                ]
            }
        ]
    )

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

    print("Setup complete.")

def start_instances(no_instances=1):
    iam = boto3.client('iam')
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    key_name = 'ec2-keypair'
    print("Starting instances...")
    
    user_data_script = """#!/bin/bash
    cd /tmp
    sudo yum update
    touch i_made_it.txt
    sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_386/amazon-ssm-agent.rpm
    sudo systemctl start amazon-ssm-agent
    cd ~
    sudo yum -y install python3
    """
    
    instances = ec2.create_instances(
        ImageId = 'ami-00e8b55a2e841be44',
        MinCount = 1,
        MaxCount = no_instances,
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
        ],
        UserData=user_data_script
        
    )

    count = 0
    for instance in instances:
        print("Starting Instance-" + str(count)+ "...")
        print("(Waiting until the instance is up and running, this may take a few moments)")
        instance.wait_until_running()
        instance.load()
        ip_address = instance.public_ip_address.replace('.','-')
        print("Instance-" + str(count) + " IP Address: " + instance.public_ip_address)
        time.sleep(12)
        os.system('scp -o "StrictHostKeyChecking no" -i %s %s ec2-user@ec2-%s.eu-west-2.compute.amazonaws.com:proof_of_work.py' % ('ec2-keypair.pem', 'proof_of_work.py', ip_address))
        # instance.terminate()
        count += 1
    
    print("Checking status of all instances...")
    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=get_instance_ids(instances))
    print("Check complete.")
    
    return instances

def get_instance_ids(instances):
    ids = []
    for instance in instances:
        ids.append(instance.instance_id)
    return ids

def terminate_instances(instances):
    for instance in instances:
        instance.terminate()

def send_commands_to_instance(instance, instance_no, commands):
    client = boto3.client('ssm')
    instance_id = instance.instance_id
    response = client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Comment="python test",
        Parameters={
            'commands': commands 
        },


    )
    print("Commands sent to Instance-" + str(instance_no) + ".")

def get_command_outputs(instances):
    client = boto3.client('ssm')
    outputs = []
    count = 0
    wait = True
    
    for i in instances:
        while wait:
            response = client.list_command_invocations(
                InstanceId=i.instance_id,
                Details=True
            )
            
            status = response['CommandInvocations'][0]['Status']
            if status == "Success":
                wait = False
            elif status == "Failed":
                wait = False
                print("Instance-" + str(count) + " Failed to run commands.")
            elif status =='TimedOut':
                wait = False
                print("Instance-" + str(count) + " Timed Out when running commands.")
                
        
        count += 1
        output = response['CommandInvocations'][0]['CommandPlugins'][0]['Output']
        print(output)
        outputs.append(output)
    
    return outputs



if not os.path.exists('ec2-keypair.pem'):
    cloud_setup()

instances = start_instances()

#TODO: want a function that divides work here
commands = ["python3 -V"]
send_commands_to_instance(instances[0], 0, commands)
time.sleep(1)
print(get_command_outputs(instances))
terminate_instances(instances)
