#!/bin/sh
aws iam remove-role-from-instance-profile --role-name "demo" --instance-profile-name "demoprofile"    
aws iam delete-instance-profile --instance-profile-name "demoprofile" 
aws iam detach-group-policy --group-name "admin" --policy-arn "arn:aws:iam::aws:policy/AdministratorAccess"
aws iam detach-role-policy --role-name "demo" --policy-arn "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
aws iam detach-role-policy --role-name "demo" --policy-arn "arn:aws:iam::aws:policy/AdministratorAccess"
aws iam delete-group --group-name "admin"                                                                                                 
aws iam delete-role --role-name "demo"                                                                                                    
aws ec2 delete-key-pair --key-name "aw16997-keypair"  
aws ec2 delete-security-group --group-name "demo_group"
rm -f ec2-keypair.pem 