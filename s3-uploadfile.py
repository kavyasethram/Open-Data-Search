import boto3

AWS_KEY = 'AKIAIKXY2T7DXZ76XVUA'
AWS_SECRET = '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'

s3_client = boto3.client('s3', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET)
s3_resource = boto3.resource('s3', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET)

s3_client.upload_file("test.jpg", "opendatasearch", "test.jpg")

object_acl = s3_resource.ObjectAcl('opendatasearch','test.jpg')
response = object_acl.put(ACL='public-read')
print(response)