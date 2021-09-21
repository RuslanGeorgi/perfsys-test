import json
import boto3
import os
import uuid


dynamodb = boto3.resource('dynamodb')


def getBlobDetails(event, context):
    table = dynamodb.Table(os.environ['MASTER_IMAGE_TABLE'])
    
    try:
    
        result = table.get_item(
            Key={
                'imageID': event['pathParameters']['imageID']
            }
        )
        
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Item'])
        }
    
    except KeyError:
        
        response = {
            "statusCode": 404,
            "body": json.dumps({'error_message': 'not found'})
        }
    
    return response