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
        # video_file = event['videoFile']
        # print(video_file)

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
    
def submit_comprehend(event, context):

    print("Received event {}".format(json.dumps(event)))
    try:
        record = event['Records'][0]        
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']

        print(s3bucket)
        print(s3object)

        s3 = boto3.resource('s3')
        content_object = s3.Object(s3bucket, s3object)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        transcript = json_content['results']['transcripts'][0]['transcript']
        print(transcript)

        client = boto3.client('comprehend')
        sentiment = client.detect_sentiment(Text=transcript,LanguageCode='en')['Sentiment']
        print(sentiment)
        
        return builder.build_response(200, json.dumps(sentiment))
    except Exception as e:
        print(e)
        raise Exception("Error submitting to the transcriber")

def analyze_transcribe(event, context):

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

        print(uname)
        print(file)


        client = boto3.client('quicksight')

        return builder.build_response(200, json.dumps({}))
    except Exception as e:
        print(e)
        raise Exception("Error submitting to the transcriber")

def get_upload_url(event, context):
    try:
        # # Get the user ID or some unique identifier for generating the S3 key
        # user_id = 'USER_ID'  # You can use Cognito username, user ID, or any other identifier
        # file_name = f'videos/{user_id}/example-video.webm'  # Customize the S3 key as needed
        # bucket_name = 'YOUR_S3_BUCKET_NAME'
        expiration = 3600  # URL expiration time in seconds (1 hour in this case)

        ts = time.time()
        headers = event['headers']
        token = headers.get('jwt', '')
        auth_header = headers.get('toast', '')
        print(auth_header)
        if auth_header.startswith('AWS'):
            _, credentials_base64 = auth_header.split(' ', 1)
            print(credentials_base64)
            try:
                # credentials_bytes = base64.b64decode(credentials_base64)
                # credentials_str = credentials_bytes.decode(errors='ignore')
                access_key_id, secret_access_key, session_token = credentials_base64.split(':')
            except Exception as e:
                # Handle any decoding or splitting errors here
                print("Error decoding credentials:", e)
                # Add any additional error handling or log the error

        decoded = jwt.decode(token, options={"verify_signature": False})
        print(decoded)

        uname = decoded['cognito:username']
        file_name = "%s/%s/%s"%("videos",uname,ts)
        print(bucket_name)
        print(file_name)

        print(access_key_id)
        print(secret_access_key)
        print(session_token)

        content_type = "video/webm"

        s3_client = boto3.client(
            "s3",
            # aws_access_key_id=access_key_id,
            # aws_secret_access_key=secret_access_key,
            # aws_session_token=session_token
        )

        # Generate the pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': bucket_name, 'Key': file_name, 'ContentType': content_type},
            ExpiresIn=expiration
        )

        return builder.build_response(200, json.dumps({'url': presigned_url}))

        # return {
        #     'statusCode': 200,
        #     'body': json.dumps({'url': presigned_url})
        # }
    except Exception as e:
        print(e)
        return builder.build_response(500, json.dumps({'body': json.dumps('Error getting pre-signed URL: ' + str(e))}))
        # return {
        #     'statusCode': 500,
        #     'body': json.dumps('Error getting pre-signed URL: ' + str(e))
        # }