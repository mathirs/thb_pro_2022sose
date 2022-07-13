from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as tasks,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam
)
from constructs import Construct


class CdkMainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db_update = _lambda.Function(
            self, 'db_update',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='db_update.lambda_handler',
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "numpy",
                    'arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-numpy:3'),
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "pandas",
                    'arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-pandas:4')
            ],
            function_name="db_update_thb",
            timeout=Duration.seconds(60)
        )

        email_generator = _lambda.Function(
            self, 'email_generator',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='email_generator.lambda_handler',
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "matplotlib",
                    'arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-matplotlib:7'),
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "docx",
                    'arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-python-docx:4')
            ],
            function_name="email_generator_thb",
            timeout=Duration.seconds(600)
        )

        accounts_table = dynamodb.Table(
            self, "Accounts_THB",
            table_name="Accounts_THB2",
            partition_key=dynamodb.Attribute(name="AccountNr", type=dynamodb.AttributeType.STRING)
        )

        costs_table = dynamodb.Table(
            self, "CostData_THB",
            table_name="CostData_THB2",
            partition_key=dynamodb.Attribute(name="AccountNr", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Date", type=dynamodb.AttributeType.STRING)
        )

        state_machine = stepfunctions.StateMachine(
            self, "StateMachine",
            definition=tasks.LambdaInvoke(self, "DB Update", lambda_function=db_update).next(
                tasks.LambdaInvoke(self, "EMail Generator", lambda_function=email_generator)
            )
        )

        trigger = events.Rule(
            self, "Scheduled Trigger",
            schedule=events.Schedule.cron(day="1", hour="1", minute="1")
        )

        trigger.add_target(targets.SfnStateMachine(state_machine))
        db_update.grant_invoke(state_machine)
        email_generator.grant_invoke(state_machine)
        costs_table.grant_full_access(db_update)
        costs_table.grant_read_data(email_generator)
        accounts_table.grant_read_data(db_update)
        accounts_table.grant_read_data(email_generator)
        db_update.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole", "ce:*"],
            resources=["*"]
        ))
        email_generator.add_to_role_policy(iam.PolicyStatement(
            actions=["ses:*"],
            resources=["*"]
        ))
