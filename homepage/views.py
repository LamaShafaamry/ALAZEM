from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated 
from ALAZEM.midlware.role_protection import IsAdminRole
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView


# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminRole])# Create your views here.
# def create_services():
#     print("Services Page")



from rest_framework import viewsets
from .models import Activities, Services, Media
from .serializers import ActivitieSerializer, ServiceSerializer, MediaSerializer

class ActivitieViewSet(APIView):
    def get(self, request):
        queryset = Activities.objects.all()
        serializer_class = ActivitieSerializer(queryset ,many=True, context = {'request': request})
        return Response(serializer_class.data, status=status.HTTP_200_OK)


class ServiceViewSet(APIView):
    def get(self, request):
        queryset = Services.objects.all()
        serializer_class = ServiceSerializer(queryset ,many=True, context = {'request': request})
        return Response(serializer_class.data, status=status.HTTP_200_OK)
