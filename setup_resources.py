import boto3
import botocore.exceptions

# Configuration
table_name = 'Recipes'
bucket_name = 'recipe-box-storage'
region_name = 'us-east-1'

# AWS Clients
dynamodb = boto3.client('dynamodb', region_name=region_name)
s3 = boto3.client('s3', region_name=region_name)

def create_dynamodb_table():
    """Creates the DynamoDB table for storing recipe metadata."""
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'RecipeID', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'RecipeID', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"DynamoDB Table '{table_name}' is being created...")
        dynamodb.get_waiter('table_exists').wait(TableName=table_name)
        print(f"DynamoDB Table '{table_name}' created successfully!")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"DynamoDB Table '{table_name}' already exists.")

def create_s3_bucket():
    """Creates the S3 bucket for storing recipe files."""
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region_name}
        )
        print(f"S3 Bucket '{bucket_name}' created successfully!")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"S3 Bucket '{bucket_name}' already exists.")
    except botocore.exceptions.ClientError as e:
        print(f"Error creating S3 bucket: {e}")

if __name__ == '__main__':
    create_dynamodb_table()
    create_s3_bucket()

