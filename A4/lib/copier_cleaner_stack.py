from aws_cdk import (
    aws_s3 as s3,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_iam as iam,
    Stack, Duration,
    aws_s3_notifications as s3_notifications
)
from constructs import Construct

class CopierCleanerStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_bucket = s3.Bucket(self, "SourceBucket")
        destination_bucket = s3.Bucket(self, "DestinationBucket")

        topic = sns.Topic(self, "S3EventTopic")
        alarm_topic = sns.Topic(self, "AlarmTopic")

        # SQS Queues
        copier_event_queue = sqs.Queue(
            self, "CopierEventQueue",
            visibility_timeout=Duration.seconds(60)
        )

        logger_event_queue = sqs.Queue(
            self, "LoggerEventQueue",
            visibility_timeout=Duration.seconds(60)
        )

        cleaner_event_queue = sqs.Queue(
            self, "CleanerEventQueue",
            visibility_timeout=Duration.seconds(300)
        )

        # Subscriptions
        topic.add_subscription(subscriptions.SqsSubscription(copier_event_queue))
        topic.add_subscription(subscriptions.SqsSubscription(logger_event_queue))
        alarm_topic.add_subscription(subscriptions.SqsSubscription(cleaner_event_queue))

        # Add permission to SQS queues to receive messages from SNS topic
        copier_event_queue.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["sqs:SendMessage"],
                effect=iam.Effect.ALLOW,
                resources=[copier_event_queue.queue_arn],
                principals=[iam.ServicePrincipal("sns.amazonaws.com")],
                conditions={
                    "ArnEquals": {"aws:SourceArn": topic.topic_arn}
                }
            )
        )

        logger_event_queue.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["sqs:SendMessage"],
                effect=iam.Effect.ALLOW,
                resources=[logger_event_queue.queue_arn],
                principals=[iam.ServicePrincipal("sns.amazonaws.com")],
                conditions={
                    "ArnEquals": {"aws:SourceArn": topic.topic_arn}
                }
            )
        )

        cleaner_event_queue.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["sqs:SendMessage"],
                effect=iam.Effect.ALLOW,
                resources=[cleaner_event_queue.queue_arn],
                principals=[iam.ServicePrincipal("sns.amazonaws.com")],
                conditions={
                    "ArnEquals": {"aws:SourceArn": alarm_topic.topic_arn}
                }
            )
        )

        # Add S3 event notification to SNS topic
        source_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.SnsDestination(topic)
        )

        # Copier Lambda
        copier_lambda = _lambda.Function(
            self, "CopierLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="copier.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "DESTINATION_BUCKET": destination_bucket.bucket_name
            }
        )
        copier_lambda.add_event_source(_lambda_event_sources.SqsEventSource(copier_event_queue))

        # Logger Lambda
        logger_lambda = _lambda.Function(
            self, "LoggerLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="logger.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "DESTINATION_BUCKET": destination_bucket.bucket_name
            }
        )
        logger_lambda.add_event_source(_lambda_event_sources.SqsEventSource(logger_event_queue))

        # Grant permissions to Copier Lambda
        source_bucket.grant_read_write(copier_lambda)
        destination_bucket.grant_read_write(copier_lambda)

        # Grant permissions to Logger Lambda
        destination_bucket.grant_read_write(logger_lambda)
        source_bucket.grant_read_write(logger_lambda)

        logger_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:PutMetricData"],
                resources=["*"],
                effect=iam.Effect.ALLOW
            )
        )

        logger_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[f"{destination_bucket.bucket_arn}/*"],
                effect=iam.Effect.ALLOW
            )
        )

        # CloudWatch Alarm
        metric = cloudwatch.Metric(
            namespace='CopierCleaner',
            metric_name='TotalTemporaryFileSize',
            dimensions_map={
                'BucketName': destination_bucket.bucket_name
            },
            period=Duration.seconds(30)
        )

        alarm = cloudwatch.Alarm(self, "TemporaryFilesSizeAlarm",
                                 metric=metric,
                                 threshold=3072,  # 3KB
                                 evaluation_periods=1,
                                 datapoints_to_alarm=1,
                                 comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
                                 )

        alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))

        # Cleaner Lambda
        cleaner_lambda = _lambda.Function(
            self, "CleanerLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="cleaner.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "DESTINATION_BUCKET": destination_bucket.bucket_name
            },
            timeout=Duration.seconds(40)
        )

        cleaner_lambda.add_event_source(_lambda_event_sources.SqsEventSource(cleaner_event_queue))

        # Grant read, write, and delete permissions to the Cleaner Lambda
        destination_bucket.grant_read_write(cleaner_lambda)
        destination_bucket.grant_delete(cleaner_lambda)

        # Add permissions for CloudWatch Alarm to publish to SNS Topic
        alarm_topic.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["sns:Publish"],
                effect=iam.Effect.ALLOW,
                resources=[alarm_topic.topic_arn],
                principals=[iam.ServicePrincipal("cloudwatch.amazonaws.com")]
            )
        )
