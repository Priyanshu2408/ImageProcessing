import boto3
from testProject.settings import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_REGION ,AWS_STORAGE_BUCKET_NAME 

s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
class UploadManager():
    def upload_csv_file(self,file_obj,file_name):
        # Upload to S3
            s3_client.upload_fileobj(
                file_obj,
                AWS_STORAGE_BUCKET_NAME,
                file_name,
                ExtraArgs={'ContentType': file_obj.content_type}
        )
    
    def upload_image(self,img_buffer,s3_key):
        s3_client.upload_fileobj(
            img_buffer,
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
            ExtraArgs={'ACL': 'public-read'}
            )

        # Construct the S3 URL of the newly uploaded image
        s3_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return s3_url

            

