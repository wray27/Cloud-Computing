import boto3


# iam = boto3.client('iam')

# ## IAM Creation
x
# # Create user
# response = iam.create_user(
#     UserName='demo'
# )

# # prints iam number amd other user details
# print(response['User']['Arn'])

# # lists user in account
# paginator = iam.get_paginator('list_users')
# for response in paginator.paginate():
#     print(response)

# # update username
# iam.update_user(
#     UserName='demo',
#     NewUserName='demo1'
# )

# # Delete a user
# iam.delete_user(
#     UserName='demo1'
# )

#