import os
import json
import base64
import boto3
import builder
import jwt
from botocore.vendored import requests
# import logging

# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

s3_client = boto3.client("s3")
bucket_name = os.getenv('BUCKET')


def get(event, context):
    # log.debug("Received event {}".format(json.dumps(event)))
    # print("Received event {}".format(json.dumps(event)))
    # print(context)
    token = event['headers']['jwt']
    decoded = jwt.decode(token, options={"verify_signature": False})
    filename = decoded['cognito:username']
    object_key = filename+"/images/profile"
    # todo: check first folder $username exists and if not create
    try:
        file_content = s3_client.get_object(
            Bucket=bucket_name, Key=object_key)["Body"].read()
        response = builder.build_response(200, base64.b64encode(file_content))
    except Exception as e:
        print(e)
        raise Exception("Error getting photo {} from {}".format(object_key, bucket_name))

    return response


def save(event, context):

    print("Received event {}".format(json.dumps(event)))

    body = event['body']
    loaded = json.loads(body)
    # print(loaded.get("body"))
    # print(base64.b64encode(requests.get(body).content))
    content = loaded.get("body")
    print(content)
    token = event['headers']['jwt']
    decoded = jwt.decode(token, options={"verify_signature": False})
    filename = decoded['cognito:username']
    object_key = filename+"/images/profile"
    try:
        file_content = s3_client.put_object(
            Bucket=bucket_name, Key=object_key, Body=base64.b64decode(content))
        response = builder.build_response(200, json.dumps("{}"))
    except ValueError as e:
        print(e)
        raise Exception("Error saving photo {} to {}".format(object_key, bucket_name))

    return response

