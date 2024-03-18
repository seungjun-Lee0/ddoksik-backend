import os
from boto3 import client

APP_ENV = os.getenv('APP_ENV', 'development')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'avocado1')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'ddoksik2.cluster-cricim2es6bi.ap-northeast-2.rds.amazonaws.com')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ddoksik2')
TEST_DATABASE_NAME = os.getenv('DATABASE_NAME', 'test_health-care')

COGNITO_USERPOOL_ID = "ap-northeast-2_zd2aqBRM4"
COGNITO_CLIENT_ID = "684v4b4ei247ojk4pnqt88tapk"
COGNITO_REGION = "ap-northeast-2"

# AWS_ACCESS_KEY_ID = "AKIAUXEEDCLZCWQ2A7KV"
# AWS_SECRET_ACCESS_KEY = "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"

cognito_client = client(
    'cognito-idp',
    region_name='ap-northeast-2',
    aws_access_key_id='AKIAUXEEDCLZCWQ2A7KV',
    aws_secret_access_key='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'
)
