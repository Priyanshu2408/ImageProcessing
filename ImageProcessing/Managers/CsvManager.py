import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
import os
from ImageProcessing.models import CSVData , Product
from testProject.Exceptions import DefaultException
from testProject.Lib.Aws.AwsUpload import UploadManager
from testProject.Lib.KafkaLib.KafkaManager import KafkaManager
from testProject.settings import AWS_STORAGE_BUCKET_NAME,AWS_REGION
from uuid import uuid4

class CsvManager():
    def validate_and_process_csv_file(self,csv_file):
        if not csv_file:
            raise DefaultException(msg="No file provided")
    
        # Ensure the uploaded file is a CSV
        if not csv_file.name.endswith('.csv'):
            raise DefaultException(msg="Invalid file type. Please upload a CSV file.")
        
        # Save the file temporarily to process it
        file_path = default_storage.save(f'temp/{uuid4()}.csv', csv_file)
        file_full_path = os.path.join(default_storage.location, file_path)
        
        try:
            # Open and validate the CSV file
            with open(file_full_path, mode='r') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)

                # Check if the header matches the expected format
                expected_header = ['Serial Number', 'Product Name', 'Input Image Urls']
                if header != expected_header:
                    raise DefaultException(msg="Invalid CSV format")                
                
                csv_data = CSVData.objects.create(status=0)
                csv_data.file_name = csv_file.name

                products = []
                for row in csv_reader:
                    # Validate each row contains valid data
                    if len(row) != 3:
                        raise DefaultException(msg=f"Invalid row: {row}")  

                    serial_number, product_name, input_image_urls = row
                    input_image_urls = input_image_urls.split(',')

                    # Basic validation for URLs (you can extend this with proper URL validation)
                    for url in input_image_urls:
                        if not url.startswith('http'):
                            raise DefaultException(msg=f"Invalid URL in row: {row}")  

                    Product.objects.create(
                        request=csv_data,
                        product_name=product_name,
                        input_image_urls=','.join(input_image_urls)
                    )
            # Uploading CSV file
            csv_data.status = 1
            csv_data.save()  
            self.upload_csv_file_and_trigger_processing(csv_file,csv_file.name,csv_data.id)
            # Remove the file after processing
            os.remove(file_full_path)
            
            # Here you can store the validated products to the database or process them further
            return Response({"message": "CSV uploaded and validated successfully", "products": products}, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Clean up if something goes wrong
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def upload_csv_file_and_trigger_processing(self,file_obj,file_name,file_id):
        upload_manager = UploadManager()
        upload_manager.upload_csv_file(file_obj,file_name)
        # Prepare the S3 file URL (assuming public access or signed URL)
        s3_file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"

        # Trigger Kafka event after upload
        kafka_message = {
            'file_name': file_obj.name,
            's3_url': s3_file_url,
            'upload_status': 'success',
            'request_id': file_id
        }
        KafkaManager().push_csv_processing_data(kafka_message)