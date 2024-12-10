#!/usr/bin/env python3

import boto3

# AWS Clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# DynamoDB Table and S3 Bucket
table_name = 'Recipes'  # Replace with your table name
bucket_name = 'recipe-box-storage'  # Replace with your bucket name

# Test DynamoDB Connection
def test_dynamodb():
    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        print(f"DynamoDB Connected! {len(response['Items'])} item(s) found in the table.")
    except Exception as e:
        print(f"Error connecting to DynamoDB: {e}")

# Test S3 Connection
def test_s3():
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            print(f"S3 Connected! {len(response['Contents'])} file(s) found in the bucket.")
        else:
            print("S3 Connected! No files found in the bucket.")
    except Exception as e:
        print(f"Error connecting to S3: {e}")

# Run tests
if __name__ == "__main__":
    test_dynamodb()
    test_s3()