from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as AuthUser 
from django.http import JsonResponse
from ALAZEM.midlware.role_protection import IsAdminManagerRole
from users.models import Role ,User , Volunteer, VolunteerStatus
from .serializers import Volunteerserializers

import json
from rest_framework import status
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import Volunteerserializers
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import get_object_or_404


from rest_framework_simplejwt.tokens import RefreshToken


""" if form.is_valid():
            user = form.save(commit=False)
            user.role_id = Role.objects.get(role_name='Admin')  # Default role
            user.save()
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

"""

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token= refresh.access_token
            access_token['role'] = user.role if user.role else None
            #access_token['role']= user.role
            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
            })
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])
def create_Volunteer(request):
    # user_data = request.data.get('user')
    # if not user_data:
    #     return Response({'error': 'User  data is required'}, status=status.HTTP_400_BAD_REQUEST)
    # Create the user
    volunteer_role = Role.VOLUNTEE  

    if volunteer_role is None:
        return Response("{'error' : 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)} {volunteer_role}")



    user = User.objects.create_user(
        username=request.data.get('username'),
        password=request.data.get('password'),
        email=request.data.get('email', ''),  # Optional email field
        first_name= request.data.get("first_name"),
        last_name= request.data.get("last_name"),
        phone = request.data.get("phone"),
        role = volunteer_role
    )


    volunteer_data = {
        "first_name": request.data.get("first_name"),
        "last_name": request.data.get("last_name"),
        "father_name": request.data.get("father_name"),
        "mother_name": request.data.get("mother_name"),
        "date_of_birth": request.data.get("date_of_birth"),
        "place_of_birth": request.data.get("place_of_birth"),
        "nationality": request.data.get("nationality"),
        "national_ID": request.data.get("national_ID"),
        "grand_history": request.data.get("grand_history"),
        "address": request.data.get("disability_card_number"),
        "certificate": request.data.get("certificate"),
        "job": request.data.get("other_disability"),
        "previously_affiliated_associations": request.data.get("previously_affiliated_associations"),
        "user_id": user.id , # Associate the patient with the newly created user
        #"status": request.data.get("status")
    }

    # Deserialize the incoming JSON data
    serializer = Volunteerserializers(data=volunteer_data)
    if serializer.is_valid():
        volunteer = serializer.save()  # Save the patient using the serializer
        return Response({'message': 'Volunteer created successfully!', 'volunteer_id': str(volunteer.id)}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_volunteer_profile(request):
    user = request.user

    if user.role != Role.VOLUNTEE:
        return Response({'error': 'Only the Owner profile can update their profile.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        volunteer = Volunteer.objects.get(user_id=user)
    except Volunteer.DoesNotExist:
        return Response({'error': 'Volunteer profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Update User fields
    user_fields = ['email' , 'first_name', 'last_name' , 'phone']
    for field in user_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()

    # Update Patient fields
    serializer = Volunteerserializers(volunteer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Your profile updated successfully.', 'data': serializer.data},
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_volunteer(request):
    volunteer_list = Volunteer.objects.all()
    name = request.query_params.get('name', None)
    job = request.query_params.get('job', None)

    if name:
        volunteer_list = volunteer_list.filter(first_name__icontains=name) | volunteer_list.filter(last_name__icontains=name) 
    if job:
        volunteer_list = volunteer_list.filter(job__icontains=volunteer_list)
        
    serializer = Volunteerserializers(volunteer_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def update_volunteer_status(request, volunteer_id):
    status_choice = request.data.get('status')

    # Ensure valid status
    if status_choice not in VolunteerStatus.values:
        return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.status = status_choice
    volunteer.save()

    serializer = Volunteerserializers(volunteer)
    return Response({'message': f'Volunteer status updated to {volunteer.status}.', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_own_profile(request):
    user = request.user

    if request.method in ['PUT', 'PATCH']:
        # Update user fields
        user_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
        for field in user_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        user.delete()
        return Response({'message': 'Your account has been deleted.'}, status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'GET':
        from .serializers import UserSerializer  # Replace with actual path
        serializer = UserSerializer(user)
        return Response(serializer.data)

    return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
