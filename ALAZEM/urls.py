from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def users(request):
    return HttpResponse("ALAZEM")

urlpatterns = [
    path('dashboared/', admin.site.urls),
    # path('', include('homepage.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('homepage/', include('homepage.urls')),
    path('users/', include('users.urls')),
    path('services/', include('services.urls')),
    path('donations/', include('donations.urls')),

]
