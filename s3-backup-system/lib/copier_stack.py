from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as actions,
    aws_iam as iam,
    Duration,
    CfnOutput,
)
from constructs import Construct

class CopierStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the buckets
        self.source_bucket = s3.Bucket(self, "SourceBucket")
        self.destination_bucket = s3.Bucket(self, "DestinationBucket")

        # Create an SNS topic for S3 events
        s3_event_topic = sns.Topic(self, "S3EventTopic")

        # Create an SQS queue for cleaner
        self.cleaner_sqs_queue = sqs.Queue(self, "CleanerSQSQueue")

        # Create an SNS topic for the alarm
        self.alarm_sns_topic = sns.Topic(self, "AlarmSNSTopic")

        # Lambda function to copy objects from source to destination
        copier_lambda = lambda_.Function(self, "CopierLambda",
                                         runtime=lambda_.Runtime.PYTHON_3_12,
                                         handler="copier.handler",
                                         code=lambda_.Code.from_asset("lambda/copier"),
                                         environment={
                                             'DESTINATION_BUCKET': self.destination_bucket.bucket_name
                                         }
                                         )

        # Lambda function to log events
        logger_lambda = lambda_.Function(self, "LoggerLambda",
                                         runtime=lambda_.Runtime.PYTHON_3_12,
                                         handler="logger.handler",
                                         code=lambda_.Code.from_asset("lambda/logger"),
                                         environment={
                                             'DESTINATION_BUCKET': self.destination_bucket.bucket_name
                                         },
                                         timeout = Duration.seconds(40)
                                         )

        # Permissions for the copier lambda function
        self.source_bucket.grant_read(copier_lambda)
        self.destination_bucket.grant_write(copier_lambda)

        # Permissions for the logger lambda function
        self.destination_bucket.grant_read(logger_lambda)
        logger_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"]
        ))

        # Add SNS subscriptions
        s3_event_topic.add_subscription(subscriptions.LambdaSubscription(copier_lambda))
        s3_event_topic.add_subscription(subscriptions.LambdaSubscription(logger_lambda))

        # Set up S3 event to invoke the SNS topic
        self.source_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.SnsDestination(s3_event_topic)
        )

        # Log group for Logger Lambda
        logs.LogGroup(self, "LoggerLogGroup",
                      log_group_name=f"/aws/lambda/{logger_lambda.function_name}",
                      retention=logs.RetentionDays.ONE_WEEK
                      )

        # Add a subscription from the alarm SNS topic to the SQS queue
        self.alarm_sns_topic.add_subscription(subscriptions.SqsSubscription(self.cleaner_sqs_queue))

        # Define the metric
        temp_metric = cloudwatch.Metric(
            namespace="S3BackupSystem",
            metric_name="TemporaryObjectSize",
            dimensions_map={"BucketName": self.destination_bucket.bucket_name},
            statistic="Sum",
            period=Duration.seconds(10)
        )

        # Create an alarm that triggers the SNS topic
        alarm = cloudwatch.Alarm(self, "TempObjectsSizeAlarm",
                                 metric=temp_metric,
                                 threshold=3072,
                                 evaluation_periods=1,
                                 datapoints_to_alarm=1,
                                 treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
                                 )
        alarm.add_alarm_action(actions.SnsAction(self.alarm_sns_topic))

        # Outputs with unique IDs
        CfnOutput(self, "DestinationBucketOutput", value=self.destination_bucket.bucket_name, export_name="DestinationBucket")
        CfnOutput(self, "AlarmSNSTopicArnOutput", value=self.alarm_sns_topic.topic_arn, export_name="AlarmSNSTopicArn")
        CfnOutput(self, "CleanerSQSQueueUrlOutput", value=self.cleaner_sqs_queue.queue_url, export_name="CleanerSQSQueueUrl")
