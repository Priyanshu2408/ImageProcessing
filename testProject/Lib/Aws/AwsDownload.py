import boto3
from testProject.settings import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_REGION ,AWS_STORAGE_BUCKET_NAME 

s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
class DownloadManager():
    def download_file(self,bucket,file_name):
        csv_obj = s3_client.get_object(Bucket=bucket, Key=file_name)
        return csv_obj