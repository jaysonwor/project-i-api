# Project I API
Serverside APIs for the Project I. 

## Local Installation
### Pre-requisites
- Serverless Framework https://www.serverless.com/framework/
- Python 3.x
- AWS CLI
### Environment Deployment
- sls deploy  -or- npx serverless deploy
    - assumes you have a ~/.aws/creds setup
#### Creational Artifacts:
- Cognito User Pool
- Cognito User Pool Client
- Cognito Identity Pool
- Lambda
- API Gateway