import boto3 
import os 
import json

iam = boto3.client('iam')

def clean():
    iam.delete_group(GroupName="admin")
    iam.remove_role_from_instance_profile(RoleName='demo', InstanceProfileName="demo_profile")
    iam.delete_instance_profile(InstanceProfileName="demo_profile")
    iam.delete_role(RoleName="demo")






response = iam.create_group(
    Path ="/",
    GroupName="admin"
)
print(response)

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

response = iam.create_role(
    RoleName='demo',
    AssumeRolePolicyDocument=json.dumps(trust_policy)    
)
print(response)

response = iam.create_instance_profile(
    InstanceProfileName="demo_profile"
)
print(response)

response = iam.add_role_to_instance_profile(
    InstanceProfileName="demo_profile",
    RoleName="demo"
)

print(response)

clean()



# ec2 = boto3.resource('ec2')





# #create a file to store key locally
# outfile = open('ec2-keypair.pem', 'w')
# key_pair = ec2.create_key_pair(KeyName='ec2-keypair')

# #capture key and store it in a file
# key_pair_out = str(key_pair.key_material)
# outfile.write(key_pair_out)

# key_pair = 'ec2-keypair'
# # security_group = ec2.SecurityGroup(
# #         id=security_group_id,
# #         ip_permissions = [{
# #             'FromPort': port_range_start,
# #             'ToPort': port_range_end
# #         }],
# #     )
# print(ec2.security_groups)
# instances = ec2.create_instances(
#     ImageId = 'ami-00a1270ce1e007c27',
#     MinCount = 1,
#     MaxCount = 1,
#     InstanceType = 't2.micro',
#     KeyName = key_pair,
#     Monitoring = {
#         'Enabled': True
#     },
#     SecurityGroupIds = ["sg-07443869"],
#     VpcId='vpc-70106618'
# ) 

# key_pair = key_pair + '.pem'

# for instance in instances:
#     instance.wait_until_running()
#     instance.load()
#     ip_address = instance.public_ip_address.replace('.','-')
#     print(ip_address)
#     os.system('scp -i %s %s ec2-user@ec2-%s.eu-west-2.compute.amazonaws.com:proof_of_work.py' % (key_pair, 'proof_of_work.py', ip_address))

