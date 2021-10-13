import json
import boto3
import os
import uuid
import re

s3 = boto3.client('s3')

def add_to_table(blobID, callback_url):
    region_name = os.environ['REGION_NAME']
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    masterImageTable = dynamodb.Table(os.environ['MASTER_IMAGE_TABLE'])
    
    item = {
                'imageID': blobID,
                'callback_url': callback_url
    }

    masterImageTable.put_item(Item=item)

def validate_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return True if re.match(regex, url) else False
    
def get_upload_url(event, context):

    bucket = os.environ['IMAGE_LABELLING_BUCKET']
    blobID = uuid.uuid1().__str__()
    
    put_url = s3.generate_presigned_url('put_object', Params={'Bucket':bucket,'Key':blobID}, ExpiresIn=3600, HttpMethod='PUT')
    
    event_parsed = json.loads(event['body'])
    callback_url = event_parsed['callback_url']
    
    if validate_url(callback_url):
        
        add_to_table(blobID, callback_url)
        
        response = {
        "statusCode": 201,
        "body": json.dumps({"URL": put_url, "blobID": blobID, "callback_url": callback_url})
        }
    
    else:
        response = {
            "statusCode": 400,
            "body": json.dumps({'description': 'Invalid callback url supplied'})
        }
    
    # response = {
        # "statusCode": 201,
        # "body": json.dumps({"URL": put_url, "blobID": blobID, "callback_url": callback_url})
    # }

    return response
