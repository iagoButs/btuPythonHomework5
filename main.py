from os import getenv

import boto3
import botocore.exceptions

AWS_REGION = getenv("AWS_REGION", "us-east-1")
s3_client = boto3.client("s3", region_name=AWS_REGION)
lambda_client=boto3.client("lambda", region_name=AWS_REGION)
lambdaZip = "lambda.zip"

def bucket_exists(bucket_name):
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as ex:
        return False

    status_code=response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code==200:
        return True
    return False

def createBucket(bucket_name):
    if not bucket_exists(bucket_name):
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully")
        except botocore.exceptions.ClientError as ex:
            print(ex)

    else:
        print(f"Bucket '{bucket_name}' already exists")


def lambdaContent():
    with open(lambdaZip, 'rb') as file_data:
        lambdaCont = file_data.read()
    return lambdaCont


def createLambdaFunc(lambda_name):
    try:
        response=lambda_client.create_function(
            FunctionName=lambda_name,
            Runtime='python3.8',
            Role='arn:aws:iam::534711623996:role/LabRole',
            Handler='lambda_function.lambda_handler',
            Code={
                'ZipFile': lambdaContent()
            }

        )
    except botocore.exceptions.ClientError as ex:
        print(ex)
    return response


def permission(bucket_name, lambda_name):
    lambda_client.add_permission(
        FunctionName=lambda_name,
        StatementId='permissionForTrigger',
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn=f'arn:aws:s3:::{bucket_name}/*'
    )


def s3Trigger(bucket_name, lambda_name):
        try:
            s3_client.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration={
                    'LambdaFunctionConfigurations': [
                        {
                            'LambdaFunctionArn': f'arn:aws:lambda:{AWS_REGION}:534711623996:function:{lambda_name}',
                            'Events': [
                                's3:ObjectCreated:*'
                            ],
                            'Filter': {
                                'Key': {
                                    'FilterRules': [
                                        {
                                            'Name': 'suffix',
                                            'Value': 'jpeg'
                                        },
                                    ]
                                },
                            },
                        },
                    ]
                },
                SkipDestinationValidation=True
            )
        except botocore.exceptions.ClientError as ex:
            print(ex)


def main(bucket_name, lambda_name):

    createBucket(bucket_name)
    createLambdaFunc(lambda_name)
    permission(bucket_name, lambda_name)
    s3Trigger(bucket_name, lambda_name)




if __name__ == '__main__':
    main("btutest123", "btutestlambda123")
