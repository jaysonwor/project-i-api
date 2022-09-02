import os, json, base64, boto3, builder, jwt, time, uuid, re
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
        uname = decoded['cognito:username']
        # filename = "433b3241-e797-4dc1-b248-2024f299dd92"
        prefix = "videos/" + uname
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
        uname = decoded['cognito:username']
        prefix = "videos/" + uname
        print(bucket_name)
        print(prefix)
        result = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix)
        print(result['Contents'])
        count = len(result['Contents'])
        print("{} videos found".format(count))
        return builder.build_response(200, json.dumps(count))
    except Exception as e:
        # just return 0 
        print(e)
        return builder.build_response(200, json.dumps(e)) 


def save(event, context):

    print("Received event {}".format(json.dumps(event)))
    try:
        data = json.loads(event['body'])
        print(data)
        data = str(data['body'])
        decoded_file = base64.b64decode(data)
        ts = time.time()

        token = event['headers']['jwt']
        decoded = jwt.decode(token, options={"verify_signature": False})
        uname = decoded['cognito:username']     
        # object_key = "%s/%s/%s.%s"%("videos",uname,ts,"mp4")
        object_key = "%s/%s/%s"%("videos",uname,ts)
        print("Saving file to: "+object_key)
    
        file_content = s3_client.put_object(
            Bucket=bucket_name, Key=object_key, Body=decoded_file)
        response = builder.build_response(200, json.dumps("{}"))

        return response
    except Exception as e:
        print(e)
        raise Exception("Error saving video {} to {}".format(object_key, bucket_name))


def submit_transcriber(event, context):

    print("Received event {}".format(json.dumps(event)))
    try:
        record = event['Records'][0]        
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']

        print(s3bucket)
        print(s3object)

        s3Path = "s3://" + s3bucket + "/" + s3object
        # jobName = s3object + '-' + str(uuid.uuid4())
        # jobName = "projectITest"
        # jobName = str(uuid.uuid4())
        parsed_folder = re.split("/", s3object)
        uname = parsed_folder[1]
        file = parsed_folder[2]

        client = boto3.client('transcribe')
      
        response = client.start_transcription_job(
        TranscriptionJobName=uname + "-" + file,
        LanguageCode='en-US',
        MediaFormat='webm',
        Media={
            'MediaFileUri': s3Path
        },
            OutputBucketName = bucket_name,
            OutputKey = "transcribe_output/"+uname+"/"
        )


        msg = {
            'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
        }

        return builder.build_response(200, json.dumps(msg))
    except Exception as e:
        print(e)
        raise Exception("Error submitting to the transcriber")
