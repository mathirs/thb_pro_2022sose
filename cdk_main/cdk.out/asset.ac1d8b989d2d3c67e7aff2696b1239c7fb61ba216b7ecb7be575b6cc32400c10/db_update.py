import boto3
import os
import uuid
import datetime
import pandas as pd
import json


def lambda_handler(event, context):
    sts = boto3.client('sts')
    dynamo = boto3.resource('dynamodb')
    accounts = dynamo.Table("Accounts_THB2")
    data = accounts.scan()['Items']
    this_account_id = context.invoked_function_arn.split(":")[4]
    for line in data:
        aws_account_id = line['AccountNr']
        credentials = None
        if aws_account_id != this_account_id:
            credentials = sts.assume_role(RoleArn=line['ARN'], RoleSessionName='CostExplorerAccess')
        request = build_request(aws_account_id, datetime.date.today())
        if credentials:
            cost_explorer = boto3.client(
                'ce',
                aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
                aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
                aws_session_token=credentials["Credentials"]["SessionToken"])
        else:
            cost_explorer = boto3.client('ce')
        cost_data = cost_explorer.get_cost_and_usage(
            TimePeriod=request['TimePeriod'], Granularity=request['Granularity'], Filter=request['Filter'], Metrics=request['Metrics'], GroupBy=request['GroupBy'])
        write_to_dynamo(cost_data, aws_account_id)
        create_history(aws_account_id, cost_explorer, dynamo.Table("CostData_THB2"))
    return {
        'statusCode': 200,
        'body': json.dumps('Dynamo !')
    }


def write_to_dynamo(event, accountnr):

    recordId = str(uuid.uuid4())
    timestamp = event["ResultsByTime"][0]["TimePeriod"]["End"]
    data = extract_cost_data(event)

    # Creating new record in DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("CostData_THB2")
    table.put_item(
        Item={
            'AccountNr' : accountnr,
            'Date' : timestamp,
            'data' : data
        }
    )

    return recordId


def build_request(account_nr, today):
    res = {'TimePeriod': {'Start': '', 'End': ''},
           'Granularity': 'MONTHLY',
           'Filter': {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': [account_nr]}},
           'Metrics': ['BlendedCost'],
           'GroupBy': [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]}
    end = datetime.date(today.year, today.month, 1)
    if today.month == 1:
        start = datetime.date(today.year - 1, 12, 1)
    else:
        start = datetime.date(today.year, today.month - 1, 1)
    res['TimePeriod']['End'] = str(end)
    res['TimePeriod']['Start'] = str(start)
    return res


def extract_cost_data(data):
    temp = data['ResultsByTime'][0]['Groups']
    df = pd.DataFrame(temp)
    res = {}
    for x in range(df.size // 2):
        if float(df.loc[x, 'Metrics']['BlendedCost']['Amount']) < 0.01:
            continue
        else:
            res[df.loc[x, 'Keys'][0]] = df.loc[x, 'Metrics']['BlendedCost']['Amount']
    return res


def create_history(account_nr, cost_explorer, table):
    date = datetime.date.today()
    if date.month > 5:
        date = datetime.date(date.year, date.month - 5, 1)
    else:
        date = datetime.date(date.year - 1, date.month + 5, 1)
    temp = table.get_item(Key={
            'AccountNr': account_nr,
            'Date': str(date)
        })
    if 'Item' not in temp:
        for x in range(5):
            if date.month + x <= 12:
                curr_date = datetime.date(date.year, date.month + x, 1)
            else:
                curr_date = datetime.date(date.year + 1, date.month + x - 12, 1)
            request = build_request(account_nr, curr_date)
            cost_data = cost_explorer.get_cost_and_usage(
                TimePeriod=request['TimePeriod'], Granularity=request['Granularity'], Filter=request['Filter'],
                Metrics=request['Metrics'], GroupBy=request['GroupBy'])
            write_to_dynamo(cost_data, account_nr)
