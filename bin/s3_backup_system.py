#!/usr/bin/env python3

from aws_cdk import App
from lib.copier_stack import CopierStack
from lib.cleaner_stack import CleanerStack

app = App()

print("Initializing CDK App")

# Deploy the CopierStack
print("Deploying CopierStack")
copier_stack = CopierStack(app, "CopierStack")
print(f"CopierStack deployed with destination bucket: {copier_stack.destination_bucket.bucket_name}")

# Deploy the CleanerStack with the name of the destination bucket from CopierStack
print("Deploying CleanerStack")
cleaner_stack = CleanerStack(app, "CleanerStack",
                             destination_bucket_name=copier_stack.destination_bucket.bucket_name)
print("CleanerStack deployed")


app.synth()

print("CDK App initialization complete")
