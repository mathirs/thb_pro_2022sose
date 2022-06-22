import boto3
import os
import uuid
import datetime
import pandas as pd
import json




def lambda_handler(event, context):
    #for multiple accounts touch up
    aws_account_id = context.invoked_function_arn.split(":")[4]
    request = build_request(aws_account_id)
    client = boto3.client('ce')
    costData = client.get_cost_and_usage(
        TimePeriod=request['TimePeriod'], Granularity=request['Granularity'], Filter=request['Filter'], Metrics=request['Metrics'], GroupBy=request['GroupBy'])
    writeToDynamo(costData, aws_account_id)
    return {
        'statusCode': 200,
        'body': json.dumps('Dynamo !')
    }


def writeToDynamo(event, accountnr):

    recordId = str(uuid.uuid4())
    timestamp = event["ResultsByTime"][0]["TimePeriod"]["End"]
    data = extract_cost_data(event)

    #Creating new record in DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("Cost_Data_thbt1")
    table.put_item(
        Item={
            'Costdata' : accountnr, #placeholder replace with account number
            'Date' : timestamp,
            'data' : data
        }
    )

    return recordId



def build_request(account_nr):
    res = {'TimePeriod': {'Start': '', 'End': ''},
           'Granularity': 'MONTHLY',
           'Filter': {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': [account_nr]}},
           'Metrics': ['BlendedCost'],
           'GroupBy': [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]}
    d = datetime.date.today()
    end = datetime.date(d.year, d.month, 1)
    start = datetime.date(d.year, d.month - 1, 1)
    res['TimePeriod']['End'] = str(end)
    res['TimePeriod']['Start'] = str(start)
    return res


def extract_cost_data(data):
    temp = data['ResultsByTime'][0]['Groups']
    df = pd.DataFrame(temp)
    res = {}
    for x in range(df.size // 2):
        if df.loc[x, 'Metrics']['BlendedCost']['Amount'] == '0':
            continue
        else:
            res[df.loc[x, 'Keys'][0]] = df.loc[x, 'Metrics']['BlendedCost']['Amount']
    return res
