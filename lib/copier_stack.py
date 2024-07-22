from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3_notifications as s3_notifications,
)
from constructs import Construct

class CopierStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the buckets
        source_bucket = s3.Bucket(self, "SourceBucket")
        destination_bucket = s3.Bucket(self, "DestinationBucket")

        # Lambda function to copy objects from source to destination
        copier_lambda = lambda_.Function(self, "CopierLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="copier.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                'DESTINATION_BUCKET': destination_bucket.bucket_name
            }
        )

        # Permissions for the lambda function
        source_bucket.grant_read(copier_lambda)
        destination_bucket.grant_write(copier_lambda)

        # Set up S3 event to invoke the lambda
        source_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(copier_lambda)
        )

        # Log group for Copier Lambda
        logs.LogGroup(self, "CopierLogGroup",
            log_group_name=f"/aws/lambda/{copier_lambda.function_name}",
            retention=logs.RetentionDays.ONE_WEEK
        )
