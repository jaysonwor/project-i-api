import json


def build_response(statusCode, body):
    response = {
        'statusCode': statusCode,
        'headers': {
            # Required for CORS support to work
            'Access-Control-Allow-Origin': '*',
            # Required for cookies, authorization headers with HTTPS
            'Access-Control-Allow-Credentials': True,
            # 'Content-Type': 'application/json'
            # "Content-Type": "text/plain"
        },
        'body': body,
        # "body": json.dumps(body)
        # 'body': "{\"errorMessage\":\"Gateway timeout\",\"errorType\":\"Gateway timeout\",\"requestId\":\"Gateway timeout\"}",        
        # 'body': json.dumps({
        #     "errorMessage": 'Missing required property',
        #     "errorType": "ApplicationError",
        #     "requestId": id
        # }),
        'isBase64Encoded': False
    }
    return response
