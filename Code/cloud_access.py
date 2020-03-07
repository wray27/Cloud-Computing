import boto3 
import os 
import json
from requests import get
import sys
import time
import argparse
import proof_of_work
import math

# this file deals with configuring the cloud and starting instances sending commands to them 
# and retrieving their output

# configuring aws group, role and user settings and the port configurations for each instance
def cloud_setup():
    iam = boto3.client('iam')
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    ip = get('https://api.ipify.org').text
    print('Your IP Address: ' + ip)

    # creating a group for user/roles to be assigned to
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

    # creating a role so that a user can assume
    # role has full administrator 
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

    # creating a profile for instances
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

    # creating security groups for the instances opens ports 
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

    # creating a key to ssh into instances then saves it to the current directory
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

# starts up aws instances
def start_instances(no_instances=1):
    iam = boto3.client('iam')
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    key_name = 'aw16997-keypair'
    print("Starting instances...")
    
    # script that is run during the instance start up have to install python and start up an SSM agent to send 
    # remote commands
    user_data_script = """#!/bin/bash
    cd /tmp
    sudo yum update
    touch i_made_it.txt
    sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_386/amazon-ssm-agent.rpm
    cd ~
    sudo yum -y install python3
    sudo systemctl start amazon-ssm-agent
  
    """
    # creates instances
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

    # waits until each instance is up and copies proof of work to each instance 
    count = 0
    for instance in instances:
        print("Starting Instance-" + str(count)+ "...")
        print("(Waiting until the instance is up and running, this may take a few moments)")
        instance.wait_until_running()
        instance.load()
        ip_address = instance.public_ip_address.replace('.','-')
        print("Instance-" + str(count) + " IP Address: " + instance.public_ip_address)
        time.sleep(12)
        os.system('scp -oUserKnownHostsFile=/dev/null  -o LogLevel=ERROR -o "StrictHostKeyChecking no" -i %s %s ec2-user@ec2-%s.eu-west-2.compute.amazonaws.com:proof_of_work.py' %
                  ('aw16997-keypair.pem', 'proof_of_work.py', ip_address))
        count += 1
    
    # checking all instances are ok
    print("Checking status of all instances...")
    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=get_instance_ids(instances))
    print("Check complete.")
    
    return instances

# gets the ids each instance in a list of instances
def get_instance_ids(instances):
    ids = []
    for instance in instances:
        ids.append(instance.instance_id)
    return ids

# terminatess each instance within a list of instances
def terminate_instances(instances):
    for instance in instances:
        instance.terminate()

# sends a unix command to a instance
def send_command_to_instance(instance, instance_no, commands):
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

# sends all generated commands to instances
def send_all_commands(instances, commands):
    count = 0
    for i in instances:
        send_command_to_instance(i, count, [commands[count]])
        count += 1

# gets the output from an instance
def get_command_output(instances):
    # returns as soon as the first vm recieves an output
    client = boto3.client('ssm')
    output = []
    wait = True

    # waits until an instance produces an putput
    while wait:
        count = 0

        # checking each instacne fora response
        for i in instances:
            response = client.list_command_invocations(
                InstanceId=i.instance_id,
                Details=True
            )
            
            # handles the response produced from an instance
            cinvs = response['CommandInvocations']
            if (cinvs):
                status = response['CommandInvocations'][0]['Status']
                if status == "Success":
                    output = response['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                    wait = False
                elif status == "Failed":
                    output = response['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                    wait = False
                    print("Instance-" + str(count) + " Failed to run commands.")
                elif status =='TimedOut':
                    wait = False
                    print("Instance-" + str(count) + " Timed Out when running commands.")
                    
                count += 1
        
    
    return output

def calculate_desired_num_of_vms(difficulty, time_limit, confidence):
    
    # number of trials that can be performed by one vm in time given
    total_trials = time_limit * 160000
    p_golden = 1 /(2**(difficulty))
    
    # expectation is set to one, giving us the expectation of trials
    expected_no_trials  =  (1 / p_golden) * confidence
    number_of_vms = expected_no_trials / total_trials
    number_of_vms = math.ceil(number_of_vms)
    
    return number_of_vms
    
# calculates the right commands to give each instance so that the work is correctly across instances
def generate_commands(number_of_vms, time_limit, difficulty, performance_flag, start_val=0):

    # finds the range of nonces to check for each instance
    commands = []
    ranges = proof_of_work.split_work(number_of_vms, time_limit, speed=150000, start_val=0)
    performance = ''
    if performance_flag: performance = ' -P '

    # produces the unix command as a string to send to each intsance
    for i in range(number_of_vms):
        command = f"python3 /home/ec2-user/proof_of_work.py {performance}-T {time_limit} -D {difficulty} -N {number_of_vms} -b {ranges[i]['Start']} -e {ranges[i]['Stop']}"
        commands.append(command)

    return commands

# runs an experiment listed in experiments.py
def run_experiment(number_of_vms, time_limit, difficulty, performance_flag=False):
    instances = start_instances(number_of_vms)
    # divides work here
    commands = generate_commands(number_of_vms, time_limit, difficulty, performance_flag=performance_flag)
    send_all_commands(instances, commands) 
    output = get_command_output(instances)
    terminate_instances(instances)
    return output

# runs multiple experiment listed in experiments.py but shanging the difficulty each time
def run_multiple_experiments(number_of_vms, time_limit, difficulty, performance_flag=False):
    instances = start_instances(number_of_vms)
    # divides work here
    result = []
    for d in range(difficulty):
        print(d+1, 'Difficulty Checked.')
        try:
            commands = generate_commands(number_of_vms, time_limit, d, performance_flag=performance_flag)
            send_all_commands(instances, commands) 
            output = get_command_output(instances)
            int_result = float(output.strip("[]\n").split(",", 1)[1])
            result.append(output)
        except:
            result.append(None)

    terminate_instances(instances)
    return result

def main(args):
    # arguments for the program
    number_of_vms = args.number_of_vms
    confidence = args.confidence
    time_limit = args.time
    difficulty = args.difficulty
    performance = args.performance

    # run the cloud setup if you cant find a key in the current directory
    if not os.path.exists('aw16997-keypair.pem'):
        cloud_setup()

    # autimatically calculates if desired number of vms if not set
    if number_of_vms == 0:
        number_of_vms = calculate_desired_num_of_vms(difficulty, time_limit, confidence)
        print(f"automatically chosen {number_of_vms} virtual machine(s) that will yield a golden nonce within {time_limit} seconds with {confidence*100}% confidence")
    
    # perform a perfrmance test to determine how many nonces can be checked per second
    if performance: 
        print("number of virtual machines has been set to 1 for performance test")
        number_of_vms = 1
    
    print(run_experiment(number_of_vms, time_limit, difficulty, performance))

if __name__ == "__main__":

    # parsing arguments for the program
    parser = argparse.ArgumentParser(
        description="Finding the golden nonce in the cloud.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-N", "--number-of-vms", help="number of vms to run the code", choices=range(51), required=False, type=int, default=0)
    parser.add_argument("-D", "--difficulty", help="difficulty",choices=range(256), type=int, default=0, required=False)
    parser.add_argument("-L", "--confidence", help="confidence level between 0 and 1", default=1, type=float, required=False)
    parser.add_argument("-T", "--time", help="time before stopping", type=int, default= 300, required=False)
    parser.add_argument("-P", "--performance", help="runs a performance test", action='store_true', default=False, required=False)

    parser.parse_args()
    main(parser.parse_args())
