import boto3


class SGClient:
    def __init__(self, group_id: str):
        self.client = boto3.client('ec2')
        self.group_id = group_id

    def set_rule(self, ip: str):
        self.client.authorize_security_group_egress(
            GroupId=self.group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 443,
                 'ToPort': 443,
                 'IpRanges': [{'CidrIp': f'{ip}/32'}]}
            ])

    def del_rule(self, ip: str):
        self.client.client.revoke_security_group_egress(
            GroupId=self.group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 443,
                 'ToPort': 443,
                 'IpRanges': [{'CidrIp': f'{ip}/32'}]}
            ])
