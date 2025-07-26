from django.utils import timezone
from django.db import models

# Create your models here.
class Services(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    title = models.CharField(max_length=255 , null= False , blank= False)
    description = models.TextField( null= False , blank= False)
    creation_date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.id} - {self.title} "
    
class Activities(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    title = models.CharField(max_length=255 , null= False , blank=False)
    description = models.TextField(null= False , blank=False)
    creation_date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.id} - {self.title} "

class Media(models.Model):
    IMAGE = 'image'
    VIDEO = 'video'

    MIME_TYPE_CHOICES = [
        ('image/jpeg', 'JPEG Image'),
        ('image/png', 'PNG Image'),
        ('image/gif', 'GIF Image'),
        ('image/webp', 'WebP Image'),
        ('video/mp4', 'MP4 Video'),
        ('video/webm', 'WebM Video'),
        ('video/ogg', 'Ogg Video'),
        ('video/x-msvideo', 'AVI Video'),
    ]

    id = models.AutoField(primary_key=True,unique=True,editable=False)
    activities = models.ForeignKey(Activities , on_delete=models.CASCADE, null=True, blank=True , related_name='activity_media')
    services = models.ForeignKey(Services , on_delete=models.CASCADE, null=True, blank=True , related_name='service_media')
    file_path = models.FileField(max_length=255)

    def __str__(self):
        name = f" {self.id}"
        if self.activities is not None:
            name += f" - Activity: {self.activities.title}"
        elif self.services is not None:
            name += f" - Service: {self.services.title}"
        return name