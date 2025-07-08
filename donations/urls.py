from django.urls import path
from .views import create_donations , change_donation_status , get_donations

urlpatterns = [
    path('donation/create/', create_donations, name='create_donations'),
    path('change/donation/status/<int:donation_id>', change_donation_status, name='change_donation_status'),
    path('get/donation/', get_donations, name='get_donations'),


]