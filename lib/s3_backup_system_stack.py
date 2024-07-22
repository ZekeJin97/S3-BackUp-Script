from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_s3_notifications as s3_notifications,
)
from constructs import Construct


class S3BackupSystemStack(Stack):

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
        log_group = logs.LogGroup(self, "CopierLogGroup",
                                  log_group_name=f"/aws/lambda/{copier_lambda.function_name}",
                                  retention=logs.RetentionDays.ONE_WEEK
                                  )

        # Metric for the size of temporary objects
        temp_metric = cloudwatch.Metric(
            namespace="S3BackupSystem",
            metric_name="TemporaryObjectSize",
            dimensions_map={"BucketName": destination_bucket.bucket_name},
            statistic="Sum"
        )

        # Alarm to trigger the cleaner lambda
        alarm = cloudwatch.Alarm(self, "TempObjectsSizeAlarm",
                                 metric=temp_metric,
                                 threshold=3 * 1024,  # 3KB
                                 evaluation_periods=1,
                                 datapoints_to_alarm=1
                                 )

        # Lambda function to clean temporary objects
        cleaner_lambda = lambda_.Function(self, "CleanerLambda",
                                          runtime=lambda_.Runtime.PYTHON_3_12,
                                          handler="cleaner.handler",
                                          code=lambda_.Code.from_asset("lambda"),
                                          environment={
                                              'DESTINATION_BUCKET': destination_bucket.bucket_name
                                          }
                                          )

        # Permissions for the lambda function
        destination_bucket.grant_read_write(cleaner_lambda)

        # Alarm action
        alarm.add_alarm_action(cw_actions.LambdaAction(cleaner_lambda))
