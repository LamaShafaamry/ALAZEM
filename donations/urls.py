from django.urls import path
from .views import complate_payment, create_donations , change_donation_status , get_donations ,varifySelectedPatient ,create_checkout_session 

urlpatterns = [
    path('donation/create/', create_donations, name='create_donations'),
    path('change/donation/status/<int:donation_id>', change_donation_status, name='change_donation_status'),
    path('get/donation/', get_donations, name='get_donations'),
    path('varify-selected-patient/donation/', varifySelectedPatient, name='varifySelectedPatient'),
    path('create-checkout-session/<int:donation_id>/', create_checkout_session, name='create-checkout-session'),
    path('complete/payment', complate_payment,name='complate_payment')
    # path('api/fake-payment/<str:signed_id>/', fake_payment_page, name='fake-payment-page'),
    # path('api/donation-payment/<str:signed_id>/', simulate_payment, name='donation-payment'),


]

