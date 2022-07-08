import json
import builder


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully1111!",
        "input": event
    }
    # body = response.toast("Go Serverless v1.0! Your function executed successfully!")

    # response1 = {
    #     "statusCode": 200,
    #     'headers': {
    #         'Access-Control-Allow-Origin': '*',
    #         'Access-Control-Allow-Credentials': True
    #     },
    #     "body": json.dumps(body)
    # }

    response = builder.build_response(200, body)

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
