import boto3
import os
import uuid
import datetime
import pandas as pd
import json


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
    for x in range(df.size // 2):
        df.loc[x, 'Metrics'] = df.loc[x, 'Metrics']['BlendedCost']['Amount']
        df.loc[x, 'Keys'] = df.loc[x, 'Keys'][0]
    return df
