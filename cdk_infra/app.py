#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.cdk_stack import AppStack

env_EU = cdk.Environment(account="773124578159", region="eu-central-1")

app = cdk.App()
AppStack(app, "cdk", env=env_EU)

app.synth()
