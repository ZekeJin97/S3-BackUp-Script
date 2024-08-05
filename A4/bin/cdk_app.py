import sys
import os
from aws_cdk import App


# Add the parent directory of 'lib' to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.copier_cleaner_stack import CopierCleanerStack

app = App()
CopierCleanerStack(app, "CopierCleanerStack")

app.synth()
