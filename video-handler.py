import os, json, base64, boto3, builder, jwt, time
# from botocore.vendored import requests
# from io import BytesIO
# import logging

# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

s3_client = boto3.client("s3")
bucket_name = os.getenv('BUCKET')


def get(event, context):
    token = event['headers']['jwt']
    decoded = jwt.decode(token, options={"verify_signature": False})
    filename = decoded['cognito:username']
    object_key = filename+"/videos/one"
    try:
        file_content = s3_client.get_object(
            Bucket=bucket_name, Key=object_key)["Body"].read()
        response = builder.build_response(200, base64.b64encode(file_content))
    except Exception as e:
        print(e)
        raise Exception("Error getting video {} from {}".format(object_key, bucket_name))

    return response


def save(event, context):

    print("Received event {}".format(json.dumps(event)))
    try:
        #get the body of the request
        data = json.loads(event['body'])
        print(data)
        #get the body json element 
        data = str(data['body'])
        #print(data)
        # decode the base64 input
        decoded_file = base64.b64decode(data)
        # ts stores the time in seconds
        ts = time.time()

        token = event['headers']['jwt']
        decoded = jwt.decode(token, options={"verify_signature": False})
        filename = decoded['cognito:username']     
        object_key = "%s/%s/%s.%s"%(filename,"videos",ts,"webm")
        print("Saving file to: "+object_key)
    
        file_content = s3_client.put_object(
            Bucket=bucket_name, Key=object_key, Body=decoded_file)
        response = builder.build_response(200, json.dumps("{}"))

        return response
    except Exception as e:
        print(e)
        raise Exception("Error saving video {} to {}".format(object_key, bucket_name))
