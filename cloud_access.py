import boto3 
import os 
import json
from requests import get
import time
import argparse
import proof_of_work

parser = argparse.ArgumentParser(
        description="Finding the golden nonce in the cloud.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
parser.add_argument("-N", "--number-of-vms", help="number of vms to run the code", choices=range(51), required=False, type=int, default=0)
parser.add_argument("-D", "--difficulty", help="difficulty",choices=range(256), type=int, default=0, required=False)
parser.add_argument("-L", "--confidence", help="confidence level between 0 and 1", default=1, type=float, required=False)
parser.add_argument("-T", "--time", help="time before stopping",choices= range(60,1801), nargs=1, type=int, default= 300, required=False)
parser.parse_args()

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

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

    key_name = 'aw16997-keypair'
    print("Creating Key Pair " + key_name + "...")
    outfile = open('aw16997-keypair.pem', 'w')
    key_pair = ec2.create_key_pair(KeyName=key_name)
    key_pair_out = str(key_pair.key_material)
    outfile.write(key_pair_out)
    outfile.close()
    os.system("chmod 400 aw16997-keypair.pem")
    print(key_name + " created and saved to local directory.")

    print("Setup complete.")

def start_instances(no_instances=1):
    iam = boto3.client('iam')
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    key_name = 'aw16997-keypair'
    print("Starting instances...")
    
    user_data_script = """#!/bin/bash
    cd /tmp
    sudo yum update
    touch i_made_it.txt
    sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_386/amazon-ssm-agent.rpm
    cd ~
    sudo yum -y install python3
    sudo systemctl start amazon-ssm-agent
  
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
        os.system('scp -oUserKnownHostsFile=/dev/null -o "StrictHostKeyChecking no" -i %s %s ec2-user@ec2-%s.eu-west-2.compute.amazonaws.com:proof_of_work.py' % ('aw16997-keypair.pem', 'proof_of_work.py', ip_address))
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

def send_command_to_instance(instance, instance_no, commands):
    client = boto3.client('ssm')
    instance_id = instance.instance_id
    response = client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Comment="python test",
        Parameters={
            'commands': commands, 
            'workingDirectory':['~']
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
            # print(response)
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
        # print(output)
        outputs.append(output)
    
    return outputs

def main(args):
    number_of_vms = args.number_of_vms
    confidence = args.confidence
    time_limit = args.time
    difficulty = args.difficulty

    if number_of_vms == 0:
        proof_of_work.main(args)
        return

    if not os.path.exists('aw16997-keypair.pem'):
        cloud_setup()

    instances = start_instances(number_of_vms)
    #TODO: want a function that divides work here
    commands = [f"python3 /home/ec2-user/proof_of_work.py -N {number_of_vms}"]
    # commands = ['whoami']
    send_command_to_instance(instances[0], 0, commands)
    time.sleep(time_limit)
    print(get_command_outputs(instances))
    terminate_instances(instances)

if __name__ == "__main__":
    main(parser.parse_args())

    
