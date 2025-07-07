from django.urls import path
from .views import LoginView, list_all_notes, add_note , create_Volunteer, list_withdrawal_requests, process_withdrawal_request, request_withdrawal ,update_volunteer_profile , get_volunteer , change_volunteer_status , assign_volunteer_to_patient


urlpatterns = [
   # path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('volunteer/create/', create_Volunteer, name='create_Volunteer'),
    path('volunteer/update/', update_volunteer_profile , name='update_volunteer_profile'),
    path('volunteer/get/', get_volunteer , name='get_volunteer'),
    path('change-volunteer-status/<int:volunteer_id>', change_volunteer_status , name='change_volunteer_status'),
    path('assign/', assign_volunteer_to_patient, name= 'assign_volunteer_to_patient'),
    path('notes/add/', add_note, name='add_note'),
    path('notes/get/', list_all_notes, name='list_all_notes'),
    path('withdrawal/request/', request_withdrawal, name='request_withdrawal'),
    path('withdrawal/process/<int:volunteer_id>/', process_withdrawal_request, name='process_withdrawal_request'),
    path('withdrawal/requests/', list_withdrawal_requests, name='list_withdrawal_requests'),


]