from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_iam as iam
from aws_solutions_constructs import aws_apigateway_lambda as apigw_lambda
from aws_solutions_constructs import aws_lambda_dynamodb as lambda_ddb


class HelloConstructsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bundling_options = core.BundlingOptions(image=_lambda.Runtime.PYTHON_3_7.bundling_docker_image,
                                                command=[
                                                    'bash', '-c',
                                                    'pip install -r requirements.txt -t /asset-output && rsync -r . /asset-output',
                                                ])
        self.hello_lambda_source_code = _lambda.Code.from_asset('lambda', bundling=bundling_options)

        self.hit_lambda_source_code = _lambda.Code.from_asset('hit_lambda', bundling=bundling_options)

        self.hello_func = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hello.handler',
            code=self.hello_lambda_source_code,
            environment={
                'testkey': 'testvalue'
            }
        )

        self.hit_func = _lambda.Function(
            self, 'HitHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hitcounter.handler',
            code=self.hit_lambda_source_code,
            environment={
                'DOWNSTREAM_FUNCTION_NAME': self.hello_func.function_name
            },
            initial_policy=[
                iam.PolicyStatement(actions=["dynamodb:PutItem", "dynamodb:DescribeTable", "dynamodb:UpdateItem"], resources=["arn:aws:dynamodb:*:*:table/Hits"])
            ]
        )

        self.hit_counter = lambda_ddb.LambdaToDynamoDB(
            self, 'LambdaToDynamoDB',
            deploy_lambda=False,
            existing_lambda_obj=self.hit_func,
            dynamo_table_props=ddb.TableProps(
                table_name='Hits',
                partition_key={
                    'name': 'path',
                    'type': ddb.AttributeType.STRING
                },
                removal_policy=core.RemovalPolicy.DESTROY
            )
        )

        self.hello_func.grant_invoke(self.hit_counter.lambda_function)

        # The code that defines your stack goes here
        apigw_lambda.ApiGatewayToLambda(self,
                                        'ApiGatewayToLambda',
                                        deploy_lambda=False,
                                        existing_lambda_obj=self.hit_counter.lambda_function,
                                        api_gateway_props=apigw.RestApiProps(
                                            default_method_options=apigw.MethodOptions(
                                                authorization_type=apigw.AuthorizationType.NONE
                                            )
                                        )
                                        )
