from django.urls import path
from .views import create_patient , create_doctor ,get_users, get_doctors , get_patients , create_appointment , approve_appointment ,update_patient_profile , update_doctor_profile ,change_patient_status

urlpatterns = [
    path('patients/create/', create_patient, name='create_patient'),
    path('patients/update/', update_patient_profile, name='update_patient_profile'),
   # path('patient/delete' , delete_patient_profile, name='delete_patient_profile'),

    path('doctor/update/', update_doctor_profile, name='update_doctor_profile'),
    path('doctor/create/', create_doctor, name='create_doctor'),
   # path('doctor/delete' , delete_doctor_profile, name='delete_doctor_profile'),

    path('patients/get/', get_patients, name='get_patients'),
    path('doctors/get/', get_doctors, name='get_doctors'),
    path('users/get/', get_users, name='get_users'),
    path('change_patient_status/<int:pending_status_id>/', change_patient_status, name='change_patient_status'),

    path('api/appointments/', create_appointment, name='create_appointment'),
    path('api/appointments/approve/<int:appointment_id>/', approve_appointment, name='approve_appointment'),

]