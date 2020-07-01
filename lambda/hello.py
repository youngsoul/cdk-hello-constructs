import json
import requests

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    url = "http://worldtimeapi.org/api/timezone/America/Chicago"
    data = requests.get(url=url)
    dt = data.json()['datetime']
    print(dt)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit {} on {}\n'.format(event['path'], dt)
    }

if __name__ == '__main__':
    x = handler({'path': 'test'}, None)
    print(x)
