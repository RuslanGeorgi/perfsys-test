import json
import boto3
import os

s3 = boto3.client('s3')

def get_upload_url(event, context):

    bucket = os.environ['IMAGE_LABELLING_BUCKET']
    key = 'testkey2'
    
    put_url = s3.generate_presigned_url('put_object', Params={'Bucket':bucket,'Key':key}, ExpiresIn=3600, HttpMethod='PUT')
    
    response = {
        "statusCode": 200,
        "body": json.dumps({"URL": put_url})
    }

    return response 