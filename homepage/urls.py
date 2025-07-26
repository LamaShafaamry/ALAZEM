from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivitieViewSet, ServiceViewSet

# router = DefaultRouter()
# router.register(r'activitie', ActivitieViewSet)
# router.register(r'service', ServiceViewSet)
# router.register(r'media', MediaViewSet)

urlpatterns = [
    path('api/activity/view/', ActivitieViewSet.as_view(), name='ActivitieViewSet'),
    path('api/service/view/', ServiceViewSet.as_view(), name='ServiceViewSet'),

]
