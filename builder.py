import json


def build_response(statusCode, body):
    response = {
        "statusCode": statusCode,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        # "body": json.dumps(body)
        "body": body
    }
    return response