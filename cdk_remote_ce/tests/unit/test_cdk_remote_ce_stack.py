import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_remote_ce.cdk_remote_ce_stack import CdkRemoteCeStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_remote_ce/cdk_remote_ce_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkRemoteCeStack(app, "cdk-remote-ce")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
