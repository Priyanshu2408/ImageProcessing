from django.core.management.base import BaseCommand
from testProject.Lib.KafkaLib.KafkaConnector import get_kafka_consumer
from ImageProcessing.models import CSVData,Product
from testProject.settings import *
from testProject.Lib.Aws.AwsDownload import DownloadManager
from testProject.Lib.Aws.AwsUpload import UploadManager
import csv
from io import StringIO
import requests
from PIL import Image
from io import BytesIO

def download_csv_from_s3(s3_url):
    try:
        # Extract bucket and file path from the URL
        bucket = AWS_STORAGE_BUCKET_NAME
        file_name = s3_url.split('/')[-1]

        # Download the file as string content
        csv_obj = DownloadManager().download_file(bucket,file_name)
        csv_content = csv_obj['Body'].read().decode('utf-8')
        return csv_content

    except Exception as e:
        raise e

# Function to process each row in the CSV
def process_csv_row(row,request):
    try:
        product_name = row[1]  # assuming product name is in second column
        input_image_urls = row[2].split(',')  # assuming URLs are in third column

        output_image_urls = []

        for image_url in input_image_urls:
            image_url = image_url.strip()  # Clean up any extra spaces
            processed_image_url = process_and_upload_image(image_url, product_name)
            
            if processed_image_url:
                output_image_urls.append(processed_image_url)
            else:
                raise Exception(f"Image processing failed for URL: {image_url}")

        # Return the processed output URLs
        Product.objects.create(csv=request,product_name = product_name,input_image_urls=input_image_urls,output_image_urls= output_image_urls)
        return True

    except Exception as e:
        raise e

# Helper function to download and compress image, then upload to S3
def process_and_upload_image(image_url, product_name):
    try:
        upload_manager = UploadManager()
        # Step 1: Download the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download image from {image_url}")

        img = Image.open(BytesIO(response.content))

        # Step 2: Resize the image by 50% (50% of original width and height)
        width, height = img.size
        new_size = (width // 2, height // 2)
        img = img.resize(new_size, Image.ANTIALIAS)

        # Step 3: Save the processed image to an in-memory buffer
        img_buffer = BytesIO()
        img_format = img.format or 'JPEG'  # Default to JPEG if format is None
        img.save(img_buffer, format=img_format)
        img_buffer.seek(0)  # Move cursor back to the beginning of the file

        # Step 4: Upload the processed image to S3
        new_image_name = f"{product_name}-{uuid.uuid4()}.{img_format.lower()}"
        s3_key = f"processed_images/{new_image_name}"
        
        s3_url = upload_manager.upload_image(img_buffer,s3_key)

        return s3_url
    except Exception as e:
        return None
    
# Function to handle Kafka message processing
def process_file(message):
    try:
        # Parse the message received from Kaka
        s3_url = message['s3_url']
        request_id = message['request_id']
        
        # Update status to 'processing' in the database
        request = CSVData.objects.get(id=request_id)
        request.status = 'processing'
        request.save()

        # Download CSV from S3
        csv_content = download_csv_from_s3(s3_url)
        
        # Process the CSV row by row
        csv_file = StringIO(csv_content)
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        # Skip the header row if present
        next(csv_reader, None)

        for row in csv_reader:
            if not process_csv_row(row,request):
                raise Exception("Row processing failed")

        # After all rows are processed successfully, update status to 'completed'
        request.status = 'completed'
        request.save()

    except Exception as e:
        # On error, update the status to 'failed'
        request.status = 'failed'
        request.save()

# Main loop to consume Kafka messages




class Command(BaseCommand):
    def handle(self, *args, **options):
        kafka_consumer = get_kafka_consumer("topic-image-processing", "image-processing-group",max_poll_interval=420000)
        #print("Membership activation kafka consumer started")
        while True:
            for message in kafka_consumer:
                process_file(message.value)
