from django.db import models
from django.utils import timezone
import random
from datetime import timedelta

def random_date():
    # start_date = timezone.now() - timedelta(days=365)
    end_date = timezone.now()
    # return start_date + (end_date - start_date) * random.random()
    return end_date


# Create your models here.
class File(models.Model):
    id = models.AutoField(primary_key=True)
    pdf_file = models.FileField(upload_to='media/',null=True)
    name = models.CharField(max_length=255)
    number_of_pages = models.IntegerField()

    def __str__(self):
        return self.name
    

class Pages(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    raw_text = models.TextField()
    date = models.DateField(default=random_date)
    is_duplicate = models.BooleanField(default=False)
    file = models.ForeignKey(File, related_name='pages', on_delete=models.CASCADE)
    splitted_image_path = models.CharField(max_length=255,null=True)  # New field
    splitted_pdf_path = models.CharField(max_length=255,null=True)  # New field

    def __str__(self):
        return self.name