from django.urls import path
from .views import LoginView , create_Volunteer ,update_volunteer_profile , get_volunteer , change_volunteer_status


urlpatterns = [
   # path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('volunteer/create/', create_Volunteer, name='create_Volunteer'),
    path('volunteer/update/', update_volunteer_profile , name='update_volunteer_profile'),
    path('volunteer/get/', get_volunteer , name='get_volunteer'),
    path('change-volunteer-status/<int:volunteer_id>', change_volunteer_status , name='change_volunteer_status'),

]