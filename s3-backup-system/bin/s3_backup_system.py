import sys
import os

# Insert the project directory into the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aws_cdk as cdk
from lib.copier_stack import CopierStack
from lib.cleaner_stack import CleanerStack

app = cdk.App()

copier_stack = CopierStack(app, "CopierStack")
cleaner_stack = CleanerStack(app, "CleanerStack")

app.synth()

