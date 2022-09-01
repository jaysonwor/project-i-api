import os, json, base64, boto3, builder, jwt, time
# from botocore.vendored import requests
# from io import BytesIO
# import logging

# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

s3_client = boto3.client("s3")
bucket_name = os.getenv('BUCKET')

def delete(event, context):
    print("Received event {}".format(json.dumps(event)))
    try:
        body = json.loads(event['body'])
        filename = body.get("url")
        response = s3_client.delete_object(Bucket=bucket_name, Key=filename)   
        return builder.build_response(200, json.dumps(response))
    except Exception as e:
        print(e)
        raise Exception("Error getting videos {}".format(bucket_name))


def list(event, context):
    print("Received event {}".format(json.dumps(event)))
    try:
        token = event['headers']['jwt']
        decoded = jwt.decode(token, options={"verify_signature": False})
        parent = decoded['cognito:username']
        # filename = "433b3241-e797-4dc1-b248-2024f299dd92"
        prefix = parent + "/videos"
        filesArr = []
        result = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix)
        files = result.get("Contents")
        for file in files:
            print(file['Key'])
            object_name = file['Key']
            response = s3_client.generate_presigned_url('get_object',Params={'Bucket': bucket_name,'Key': object_name})
            print(response)
            # filesArr.append(response) todo
            filesArr.append({file['Key']: response})
        
        return builder.build_response(200, json.dumps(filesArr))
    except Exception as e:
        print(e)
        raise Exception("Error getting videos {}".format(bucket_name))


def count(event, context):
    print("Received event {}".format(json.dumps(event)))
    try:
        token = event['headers']['jwt']
        decoded = jwt.decode(token, options={"verify_signature": False})
        parent = decoded['cognito:username']
        prefix = parent + "/videos"
        result = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix)
        print(result['Contents'])
        # print(len(result['Contents']))
        count = len(result['Contents'])
        return builder.build_response(200, json.dumps(count))
    except Exception as e:
        # just return 0 
        return builder.build_response(200, json.dumps(0)) 


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
        parent = decoded['cognito:username']     
        object_key = "%s/%s/%s.%s"%(parent,"videos",ts,"mp4")
        print("Saving file to: "+object_key)
    
        file_content = s3_client.put_object(
            Bucket=bucket_name, Key=object_key, Body=decoded_file)
        response = builder.build_response(200, json.dumps("{}"))

        return response
    except Exception as e:
        print(e)
        raise Exception("Error saving video {} to {}".format(object_key, bucket_name))
