from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    Duration
)
from constructs import Construct

class CleanerStack(Stack):

    def __init__(self, scope: Construct, id: str, destination_bucket_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Metric for the size of temporary objects
        temp_metric = cloudwatch.Metric(
            namespace="S3BackupSystem",
            metric_name="TemporaryObjectSize",
            dimensions_map={"BucketName": destination_bucket_name},
            statistic="Sum",
            period=Duration.seconds(10)
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
                                              'DESTINATION_BUCKET': destination_bucket_name
                                          }
                                          )

        # Permissions for the lambda function
        cleaner_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:ListBucket", "s3:DeleteObject"],
            resources=[f"arn:aws:s3:::{destination_bucket_name}", f"arn:aws:s3:::{destination_bucket_name}/*"]
        ))

        # Alarm action
        alarm.add_alarm_action(cw_actions.LambdaAction(cleaner_lambda))

        # Log for Cleaner Lambda
        logs.LogGroup(self, "CleanerLogGroup",
                      log_group_name=f"/aws/lambda/{cleaner_lambda.function_name}",
                      retention=logs.RetentionDays.ONE_WEEK
                      )
