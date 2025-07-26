from django.contrib import admin
from .models import Donation , PatientDonation 

admin.site.register(Donation)
admin.site.register(PatientDonation)
# admin.site.register(DonationType)
# admin.site.register(DonationStatus)

# Register your models here.
