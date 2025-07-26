from django.urls import path
from .views import registration_doctor,change_doctor_status, get_my_donations, get_doctor_profile,get_patient_profile,create_patient , create_doctor ,get_users, get_doctors , get_patients , create_appointment , update_appointment_status ,update_patient_profile , update_doctor_profile ,change_patient_status ,update_medical_report , doctor_appointments , get_all_appointments , get_patient_appointments , cancel_appointments,set_doctor_password

urlpatterns = [
    path('patients/create/', create_patient, name='create_patient'),
    path('patient-profile/get/', get_patient_profile, name='get_patient_profile'),

    path('patients/update/', update_patient_profile, name='update_patient_profile'),
   # path('patient/deactivate' , deactivate_patient_profile, name='deactivate_patient_profile'),
    path('get/patient/appointments/', get_patient_appointments, name='get_patient_appointments'),

    path('doctor/update/', update_doctor_profile, name='update_doctor_profile'),
    path('doctor/create/', create_doctor, name='create_doctor'),
    path('change/doctor/status/<int:doctor_id>' , change_doctor_status, name='change_doctor_status'),
    path('doctor/appointments/', doctor_appointments, name='doctor-appointments'),


    path('patients/get/', get_patients, name='get_patients'),
    path('doctors/get/', get_doctors, name='get_doctors'),
    path('doctor-profile/get/', get_doctor_profile, name='get_doctor_profile'),

    path('users/get/', get_users, name='get_users'),
    path('appointment/get/', get_all_appointments, name='get_all_appointments'),
    path('change_patient_status/<int:patient_id>/', change_patient_status, name='change_patient_status'),

    path('api/create/appointments/', create_appointment, name='create_appointment'),
    path('appointments/<int:appointment_id>/status/', update_appointment_status, name='update_appointment_status'),
    path('appointments/<int:appointment_id>/medical-report/', update_medical_report, name='update-medical-report'),

    path('my-donation/get', get_my_donations, name='get_my_donations'),
    path('cancel/appointment/<int:appointment_id>/', cancel_appointments, name='cancel_appointments'),
    path('set/doctor/password/', set_doctor_password, name='set_doctor_password'),
    
    path('registration/doctor/', registration_doctor, name='registration_doctor'),



]