import json
import os
import boto3
from HitModel import HitModel

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['DDB_TABLE_NAME'])
_lambda = boto3.client('lambda')


def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    path_value = event['path']
    if path_value.startswith('/pynamodb'):
        try:
            hitmodel = HitModel.get(path_value)
            r = hitmodel.update(actions=[HitModel.hits.add(1)])
            print(f"Update response: {r}")
        except:
            print(f"Could not find path: {path_value}")
            hitmodel = HitModel(path_value)
            r = hitmodel.save()
            print(f"Save response: {r}")

    else:
        table.update_item(
            Key={'path': event['path']},
            UpdateExpression='ADD hits :incr',
            ExpressionAttributeValues={':incr': 1}
        )

    resp = _lambda.invoke(
        FunctionName=os.environ['DOWNSTREAM_FUNCTION_NAME'],
        Payload=json.dumps(event),
    )

    body = resp['Payload'].read()

    print('downstream response: {}'.format(body))
    return json.loads(body)
