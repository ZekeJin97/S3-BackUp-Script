from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3_notifications as s3_notifications,
)
from constructs import Construct

class CopierStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the buckets
        self.source_bucket = s3.Bucket(self, "SourceBucket")
        self.destination_bucket = s3.Bucket(self, "DestinationBucket")

        # Lambda function to copy objects from source to destination
        copier_lambda = lambda_.Function(self, "CopierLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="copier.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                'DESTINATION_BUCKET': self.destination_bucket.bucket_name
            }
        )

        # permissions
        copier_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"]
        ))

        # Permissions
        self.source_bucket.grant_read(copier_lambda)
        self.destination_bucket.grant_write(copier_lambda)

        # S3 event to invoke the lambda
        self.source_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(copier_lambda)
        )

        # Log for Copier Lambda
        logs.LogGroup(self, "CopierLogGroup",
            log_group_name=f"/aws/lambda/{copier_lambda.function_name}",
            retention=logs.RetentionDays.ONE_WEEK
        )
