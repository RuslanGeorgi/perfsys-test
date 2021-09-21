import json
import boto3
import os
import uuid

s3 = boto3.client('s3')

def get_upload_url(event, context):

    bucket = os.environ['IMAGE_LABELLING_BUCKET']
    blobID = uuid.uuid1().__str__()
    
    put_url = s3.generate_presigned_url('put_object', Params={'Bucket':bucket,'Key':blobID}, ExpiresIn=3600, HttpMethod='PUT')
    
    response = {
        "statusCode": 201,
        "body": json.dumps({"URL": put_url, "blobID": blobID})
    }

    return response
