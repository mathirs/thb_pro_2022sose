import boto3
import os
import uuid

#implement getcostandusage api to get json

def writeToDynamo(event, context):

    recordId = str(uuid.uuid4())
    timestamp = event["ResultsByTime"]["TimePeriod"]["End"]
    data = event["ResultsByTime"][0]["Groups"]

    #Creating new record in DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    table.put_item(
        Item={
            'id' : recordId, #placeholder replace with account number
            'timestamp' : timestamp,
            'data' : data
        }
    )

    return recordId