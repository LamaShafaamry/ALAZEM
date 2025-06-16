from django.db import models
from services.models import Patient
from django.utils import timezone


class DonationStatus(models.TextChoices):
    APPROVAL = 'APP', 'Approval'
    PENDING = 'PEN', 'Pending'
    REJECTED = 'REJ', 'Rejected'


class DonationType(models.TextChoices):
   ASSOCIATION = 'ASS', 'Association'
   INDIVIDUAL = 'IND', 'Individual'


class Donation(models.Model):
   id = models.AutoField(primary_key=True,unique=True,editable=False)
   donation_type = models.CharField(
      max_length=3,
      choices=DonationType.choices,
      default=DonationType.ASSOCIATION
   )
   donation_status = models.CharField(
            max_length=3,
            choices=DonationStatus.choices,
            default=DonationStatus.PENDING,
    )
   amount = models.DecimalField(max_digits=10, decimal_places=2) 
   creation_date= models.DateTimeField(default=timezone.now())

   def __str__(self):
      return f"{self.id} - {self.donation_type}"

class PatientDonation(models.Model):
   id = models.AutoField(primary_key=True,unique=True,editable=False)
   patient_id =models.ForeignKey(Patient , on_delete= models.CASCADE, blank=False , null= False)
   donation_id = models.ForeignKey(Donation, on_delete=models.CASCADE,  blank=False , null= False)
   amount = models.DecimalField(max_digits=10, decimal_places=2) 

   def __str__(self):
      return f"{self.patient_id}"

