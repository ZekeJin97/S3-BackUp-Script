from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct


class CopierStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the buckets
        self.source_bucket = s3.Bucket(self, "SourceBucket")
        self.destination_bucket = s3.Bucket(self, "DestinationBucket")

        # Create an SQS queue
        self.cleaner_sqs_queue = sqs.Queue(self, "CleanerSQSQueue")

        # Create an SNS topic
        self.alarm_sns_topic = sns.Topic(self, "AlarmSNSTopic")

        # Lambda function to copy objects from source to destination
        copier_lambda = lambda_.Function(self, "CopierLambda",
                                         runtime=lambda_.Runtime.PYTHON_3_12,
                                         handler="copier.handler",
                                         code=lambda_.Code.from_asset("lambda/copier"),
                                         environment={
                                             'DESTINATION_BUCKET': self.destination_bucket.bucket_name,
                                             'LOGGER_LAMBDA_NAME': "LoggerLambda"
                                         }
                                         )

        # Permissions for the copier lambda function
        self.source_bucket.grant_read(copier_lambda)
        self.destination_bucket.grant_write(copier_lambda)

        # Grant CloudWatch permissions
        copier_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"]
        ))

        # Set up S3 event to invoke the copier lambda
        self.source_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(copier_lambda)
        )

        # Log group for Copier Lambda
        logs.LogGroup(self, "CopierLogGroup",
                      log_group_name=f"/aws/lambda/{copier_lambda.function_name}",
                      retention=logs.RetentionDays.ONE_WEEK
                      )

        # Add a subscription from the SNS topic to the SQS queue
        self.alarm_sns_topic.add_subscription(subscriptions.SqsSubscription(self.cleaner_sqs_queue))

        # Define the metric
        temp_metric = cloudwatch.Metric(
            namespace="S3BackupSystem",
            metric_name="TemporaryObjectSize",
            dimensions_map={"BucketName": self.destination_bucket.bucket_name},
            statistic="Sum",
            period=Duration.minutes(1)
        )

        # Create an alarm that triggers the SNS topic
        alarm = cloudwatch.Alarm(self, "TempObjectsSizeAlarm",
                                 metric=temp_metric,
                                 threshold=3072,
                                 evaluation_periods=1,
                                 datapoints_to_alarm=1,
                                 treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                                 )
        alarm.add_alarm_action(cw_actions.SnsAction(self.alarm_sns_topic))

        # Logger Lambda function to create CloudWatch metric for temp objects
        logger_lambda = lambda_.Function(self, "LoggerLambda",
                                         runtime=lambda_.Runtime.PYTHON_3_12,
                                         handler="logger.handler",
                                         code=lambda_.Code.from_asset("lambda/logger"),
                                         environment={
                                             'DESTINATION_BUCKET': self.destination_bucket.bucket_name
                                         }
                                         )

        # Permissions for the logger lambda function
        self.destination_bucket.grant_read(logger_lambda)

        # Log group for Logger Lambda
        logs.LogGroup(self, "LoggerLogGroup",
                      log_group_name=f"/aws/lambda/{logger_lambda.function_name}",
                      retention=logs.RetentionDays.ONE_WEEK
                      )

        # Export the destination bucket name
        CfnOutput(self, "DestinationBucketExport", value=self.destination_bucket.bucket_name, export_name="DestinationBucketName")
