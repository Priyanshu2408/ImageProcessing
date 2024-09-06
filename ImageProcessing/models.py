from django.db import models
import uuid
# Create your models here.


class CSVData(models.Model):
    STATUS_CHOICES= (("pending",0),("processing",1),("completed",2),("failed",3))
    
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(default='', max_length=100)
    status = models.IntegerField(default=0,choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'csv_files'
        

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    csv = models.ForeignKey(CSVData, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=255)
    input_image_urls = models.TextField()
    output_image_urls = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'products'    