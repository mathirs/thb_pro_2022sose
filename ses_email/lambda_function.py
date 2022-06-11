import json
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    
    
    emailData = event['Records'][0]["messageAttributes"]
    # print(emailData['fromName'])
    
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = emailData['fromName']['stringValue'] + " <marketing@example.com>"


    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = emailData['toEmail']['stringValue']
    
    print (emailData)
    
    if 'toCCEmail' in emailData:
      CC_RECIPIENT = emailData['toCCEmail']['stringValue']
      DESTINATION={
                        'ToAddresses': [
                            RECIPIENT,
                        ],
                        'CcAddresses': [
                            CC_RECIPIENT,
                        ],
                        'BccAddresses': [
                            'marketingcc@example.com',
                        ]
                    }
      
    else:
      DESTINATION = {
                        'ToAddresses': [
                            RECIPIENT,
                        ],
                        'BccAddresses': [
                            'marketingcc@example.com',
                        ]
                    }
    
    
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "ap-southeast-2"
    
    # The subject line for the email.
    SUBJECT = emailData['subject']['stringValue']
    
    # The email body for recipients with non-HTML email clients.
    # BODY_TEXT = ("Amazon SES Test (Python)\r\n"
    #              "This email was sent with Amazon SES using the "
    #              "AWS SDK for Python (Boto)."
    #             )
                
    # The HTML body of the email.
    BODY_HTML = emailData['body']['stringValue']          
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination = DESTINATION,
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    # 'Text': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_TEXT,
                    # },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:")
        print(response['MessageId'])
        print(RECIPIENT)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    
