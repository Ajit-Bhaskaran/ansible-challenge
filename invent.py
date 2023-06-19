#!/usr/bin/env python3

import boto3
import json
import yaml

# AWS region
aws_region = 'us-east-1'

# SSH username and private key path
ansible_user = 'ec2-user'
private_key_path = 'myexp.pem'

# Create an EC2 client
ec2_client = boto3.client('ec2', region_name=aws_region)

# Retrieve EC2 instance information
response = ec2_client.describe_instances()

# Prepare the inventory dictionary
inventory = {
    'all': {
        'children': {
            'web1': {
                'hosts': {}
            },
            'web2': {
                'hosts': {}
            }
        }
    }
}

# Loop through the instances and populate the inventory
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        state = instance['State']['Name']
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        if state == 'running':
            if 'web1' in tags.get('Name', ''):
                inventory['all']['children']['web1']['hosts'][instance_id] = {
                    'ansible_host': instance['PublicIpAddress'],
                    'ansible_user': ansible_user,
                    'ansible_ssh_private_key_file': private_key_path
                }
            if 'web2' in tags.get('Name', ''):
                inventory['all']['children']['web2']['hosts'][instance_id] = {
                    'ansible_host': instance['PublicIpAddress'],
                    'ansible_user': ansible_user,
                    'ansible_ssh_private_key_file': private_key_path
                }

# Write the inventory to the file
with open('inventory/inventory.yml', 'w') as inventory_file:
    inventory_file.write(yaml.dump(inventory))

# Output the inventory dictionary as JSON
print(json.dumps(inventory))
