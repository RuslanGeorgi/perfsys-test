import json
import boto3
import os
import uuid

def labelOnS3Upload(event, context):
    bucket = os.environ['IMAGE_LABELLING_BUCKET']
    region_name = os.environ['REGION_NAME']

    filesUploaded = event['Records']
    for file in filesUploaded:
        fileName = file["s3"]["object"]["key"]
        rekognitionClient = boto3.client('rekognition', region_name=region_name)
        response = rekognitionClient.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':fileName}},
            MaxLabels=5)

        imageLabels = []

        for label in response['Labels']:
            imageLabels.append(label["Name"].lower())

    # Add to DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=region_name)

    addImageDataToMasterTableResponse = addImageDataToMasterTable(dynamodb=dynamodb, imageID=fileName, fileName=fileName,
                                                                  labels=imageLabels)

    addToLabelMappingTableResponse = addToLabelMappingTable(dynamodb=dynamodb, imageID=fileName, fileName=fileName,
                                                            imageLabels=imageLabels)

    s3HandlerResponseBody = {
        "addImageDataToMasterTableResponse": addToLabelMappingTableResponse,
        "addToLabelMappingTableResponse": addToLabelMappingTableResponse
    }

    finalResponse = {
        "statusCode": 200,
        "body": json.dumps(s3HandlerResponseBody)
    }
    return finalResponse



def addImageDataToMasterTable(dynamodb, imageID, fileName, labels):
    masterImageTable = dynamodb.Table(os.environ['MASTER_IMAGE_TABLE'])
    item = {
                'imageID': imageID,
                'fileName': fileName,
                'labels': labels
    }

    # add image data to master MASTER_IMAGE_TABLE
    masterImageTable.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response

def addToLabelMappingTable(dynamodb, imageID, fileName, imageLabels):
    labelToS3MappingTable = dynamodb.Table(os.environ['S3_MAPPING_TABLE'])
    labelResponses = []
    imageIDSet = set()
    imageIDSet.add(imageID)

    for label in imageLabels:
        addLabelResponse = labelToS3MappingTable.update_item(
            Key={'label': label},
            UpdateExpression="ADD imageIDs :imageID",
            ExpressionAttributeValues={":imageID":imageIDSet}
        )
        labelResponses.append(addLabelResponse)

    labelToS3MappingTableResponse = {
        "labelResponses": labelResponses
    }

    return labelToS3MappingTableResponse
