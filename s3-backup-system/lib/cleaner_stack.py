from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
    Duration,
    Fn
)
from constructs import Construct

class CleanerStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        destination_bucket_name = Fn.import_value("DestinationBucket")
        cleaner_sqs_queue_url = Fn.import_value("CleanerSQSQueueUrl")
        alarm_sns_topic_arn = Fn.import_value("AlarmSNSTopicArn")

        # Lambda function to clean temporary objects
        cleaner_lambda = lambda_.Function(self, "CleanerLambda",
                                          runtime=lambda_.Runtime.PYTHON_3_12,
                                          handler="cleaner.handler",
                                          code=lambda_.Code.from_asset("lambda/cleaner"),
                                          environment={
                                              'DESTINATION_BUCKET': destination_bucket_name
                                          }
                                          )

        # Add permissions to the Lambda function
        cleaner_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:DeleteObject"],
            resources=[f"arn:aws:s3:::{destination_bucket_name}/*"]
        ))

        # Construct the queue ARN using CloudFormation intrinsic functions
        queue_arn = Fn.sub("arn:aws:sqs:${AWS::Region}:${AWS::AccountId}:${QueueName}", {
            "QueueName": Fn.select(4, Fn.split("/", cleaner_sqs_queue_url))
        })

        cleaner_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
            resources=[queue_arn]
        ))

        # Alarm action
        sns.Topic.from_topic_arn(self, "CleanerAlarmSNSTopic", alarm_sns_topic_arn).add_subscription(
            subscriptions.LambdaSubscription(cleaner_lambda)
        )

        # Log group for Cleaner Lambda
        logs.LogGroup(self, "CleanerLogGroup",
                      log_group_name=f"/aws/lambda/{cleaner_lambda.function_name}",
                      retention=logs.RetentionDays.ONE_WEEK
                      )
