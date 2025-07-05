from django.urls import path
from .views import create_patient , create_doctor ,get_users, get_doctors , get_patients , create_appointment , update_appointment_status ,update_patient_profile , update_doctor_profile ,change_patient_status ,update_medical_report , doctor_appointments , get_all_appointments , patient_approved_appointments

urlpatterns = [
    path('patients/create/', create_patient, name='create_patient'),
    path('patients/update/', update_patient_profile, name='update_patient_profile'),
   # path('patient/deactivate' , deactivate_patient_profile, name='deactivate_patient_profile'),
    path('patient/appointments/', patient_approved_appointments, name='patient-approved-appointments'),

    path('doctor/update/', update_doctor_profile, name='update_doctor_profile'),
    path('doctor/create/', create_doctor, name='create_doctor'),
   # path('doctor/deactivate' , deactivate_doctor_profile, name='deactivate_doctor_profile'),
    path('doctor/appointments/', doctor_appointments, name='doctor-appointments'),


    path('patients/get/', get_patients, name='get_patients'),
    path('doctors/get/', get_doctors, name='get_doctors'),
    path('users/get/', get_users, name='get_users'),
    path('appointment/get/', get_all_appointments, name='get_all_appointments'),
    path('change_patient_status/<int:pending_status_id>/', change_patient_status, name='change_patient_status'),

    path('api/create/appointments/', create_appointment, name='create_appointment'),
    path('appointments/<int:appointment_id>/status/', update_appointment_status, name='update_appointment_status'),
    path('appointments/<int:appointment_id>/medical-report/', update_medical_report, name='update-medical-report'),

]