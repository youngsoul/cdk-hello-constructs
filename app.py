#!/usr/bin/env python3

from aws_cdk import core

from hello_constructs.hello_constructs_stack import HelloConstructsStack


app = core.App()
HelloConstructsStack(app, "hello-constructs")

app.synth()
