from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam
)
from constructs import Construct


class CdkRemoteCeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(
            self, 'ExternalCE',
            assumed_by=iam.AccountPrincipal('960901075320'),
        )

        role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=['ce:GetCostAndUsage'],
                resources=['*'],
            )
        )

