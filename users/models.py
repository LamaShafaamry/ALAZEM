from django.db import models
from django.contrib.auth.models import User ,AbstractUser
from django.db import models


import uuid

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Role(models.TextChoices):
       ADMIN =  'ADM', 'Admin'
       MANAGER = 'MAN' , ' Manager'      
       DONATIONMANAGER = 'DMA', 'DonationManager'
       DOCTOR  = 'DOC' , 'Doctor'    
       PATIENT = 'PAT' , 'Patient'
       VOLUNTEE = 'VOL', 'Volunteer'
       USER = 'USE' , 'USER'


   
class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        null=True, blank=True, upload_to='profiles/', default='profiles/user-default.png')
    role = models.CharField(
            max_length=3,
            choices=Role.choices,
            default=Role.USER,

    )
    def __str__(self):
            return self.username




class VolunteerStatus(models.TextChoices):
    REGISTERED = 'REG', 'Registered'
    PENDING = 'PEN', 'Pending'
    REJECTED = 'REJ', 'Rejected'
    WITHDRAWN = 'WIT', 'Withdrawn'



class Volunteer(models.Model):
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    nationality_ID = models.CharField(max_length=100, blank=True, null=True)
    grand_history = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    certificate = models.TextField(blank=True, null=True)
    job = models.CharField(max_length=255, blank=True, null=True)
    previously_affiliated_associations = models.TextField(blank=True, null=True)
    status = models.CharField(
            max_length=3,
            choices=VolunteerStatus.choices,
            default=VolunteerStatus.PENDING,
    )

    def __str__(self):
        return f"{self.id} - {self.first_name} {self.last_name}"



"""
class Position(models.Model):
    STAFF_POSITION =[

    ]
    models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    joining_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Staff: {self.user.username}"#
    

"""