from django.urls import path
from .views import create_donations

urlpatterns = [
    path('donation/create/', create_donations, name='create_donations'),
]