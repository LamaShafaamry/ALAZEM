from django.forms import ValidationError
from django.utils import timezone
import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as AuthUser 
from django.http import JsonResponse
from ALAZEM.midlware.role_protection import IsAdminManagerRole, IsManagerRole, IsPatientRole , IsVolunteerRole
from services.models import Patient, PatientStatus, PendingPatientStatus, RegistrationPatientStatus, WithdrawalPatientStatus
from services.serializers import PatientStatusSerializers
from users.models import Note, Role ,User , Volunteer, VolunteerStatus, WithdrawalRequest, WithdrawalrStatus
from .serializers import ForgetPasswordRequestSerializer, NoteSerializer, UserSerializer, Volunteerserializers , VolunteerAssignmentSerializer, WithdrawalRequestSerializer, WithdrawalRequestSerializerForManager

# import json
from rest_framework import status
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import Volunteerserializers
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password


from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token= refresh.access_token
            access_token['role'] = user.role if user.role else None
            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
                'role' : user.role 
            })
        else:
            return Response({"detail": "Incorrect username or password"}, status=status.HTTP_401_UNAUTHORIZED)



class ForgetPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                varification_code = f"{random.randint(100000, 999999)}"
                user.varification_code = varification_code
                user.save()

                try:
                    send_mail(
                    subject="Your Password Reset Verification Code",
                    message=f"Hello {user.first_name} {user.last_name},\n\nYour password reset verification code is: {varification_code}\n\n",
                    from_email="alazem.noreply@gmail.com", 
                    recipient_list=[email],
                    fail_silently=False,
                )
                except:
                    pass
                return Response({"detail": "Verification code sent to your email."})
            except User.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=404)
        return Response(serializer.errors, status=400)



class ResetNewPasswordView(APIView):
    def post(self, request):

        try:
            validate_password(request.data.get("new_password"))  # Optional: pass user=User instance if needed
        except ValidationError as e:
            return Response(
                {"errors": e.messages},  # Returns a list of validation messages
                status=status.HTTP_400_BAD_REQUEST
            )
        email = request.data.get('email')
        varification_code = request.data.get('varification_code')
        new_password = request.data.get('new_password')
        try:
            user = User.objects.get(email=email)
            if str(user.varification_code).strip() == str(varification_code).strip():
                user.set_password(new_password)
                user.save()
                #reset_code.delete()  # Optional: remove the code after use
                return Response({"detail": "Password has been reset."})
            else:
                return Response({"detail": "Invalid or expired code."}, status=400)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=404)
    



@api_view(['POST'])
def create_Volunteer(request):
    volunteer_role = Role.VOLUNTEE  

    if volunteer_role is None:
        return Response("{'error' : 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)} {volunteer_role}")


    if User.objects.filter(email=request.data.get('email')).exists():
        return Response("{'error' : 'A user with this email already exists.'}") 
    
    try:
        validate_password(request.data.get("password"))  # Optional: pass user=User instance if needed
    except ValidationError as e:
        return Response(
            {"errors": e.messages},  # Returns a list of validation messages
            status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.create_user(
        username=request.data.get('email'),
        password=request.data.get('password'),
        email=request.data.get('email'), 
        first_name= request.data.get("first_name"),
        last_name= request.data.get("last_name"),
        phone = request.data.get("phone"),
        role = volunteer_role,
        is_active = False,
        is_email_varification = False
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
    }

    # Deserialize the incoming JSON data
    serializer = Volunteerserializers(data=volunteer_data)
    if serializer.is_valid():
        user = User.objects.get(email=user.email)
        varification_code = f"{random.randint(100000, 999999)}"
        user.varification_code = varification_code
        user.save()
        volunteer = serializer.save()  # Save the patient using the serializer
        
        try:
            send_mail(
                        subject="Your Password Reset Verification Code",
                        message=f"Hello {user.username},\n\nYour password reset verification code is: {varification_code}\n\nIt expires in 10 minutes.",
                        from_email="alazem.noreply@gmail.com", 
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
        except:
            pass
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
def get_volunteer(request):
    print("Momin")
    volunteer_list = Volunteer.objects.filter(user_id__is_email_varification = True)
    status_filter =request.query_params.get('status_filter', None)
    name = request.query_params.get('name', None)
    job = request.query_params.get('job', None)
    # print (VolunteerStatus.PENDING)
    if name:
        volunteer_list = volunteer_list.filter(first_name__icontains=name) | volunteer_list.filter(last_name__icontains=name) 
    if job:
        volunteer_list = volunteer_list.filter(job__icontains=volunteer_list)
    if status_filter and (status_filter == VolunteerStatus.PENDING or status_filter == VolunteerStatus.REGISTERED or status_filter == VolunteerStatus.REJECTED or status_filter== VolunteerStatus.WITHDRAWN):
        volunteer_list = volunteer_list.filter(status = status_filter)

    serializer = Volunteerserializers(volunteer_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  
class VarifyAccount(APIView):
    def post(self, request):
        
        email = request.data.get('email')
        varification_code = request.data.get('varification_code')
        try:
            user = User.objects.get(email=email)
            if str(user.varification_code).strip() == str(varification_code).strip():
                user.is_email_varification = True
                user.save()
                if user.role == Role.PATIENT:
                    PatientStatus_data = {
                        "patient_id" :user.patient_user.id
                    }
                    if  user.patient_user.patient_status.first() is None:
                        PatientStatusSerializer = PatientStatusSerializers(data=PatientStatus_data)
                        if PatientStatusSerializer.is_valid():
                            patientStatus = PatientStatusSerializer.save()
                            print(patientStatus)
                        if  user.patient_user.patient_status.first().pending_statuses.first() is None:
                           pending= PendingPatientStatus.objects.create(patientStatus = patientStatus , date = timezone.now())
                           pending.save()
                #reset_code.delete()  # Optional: remove the code after use
                return Response({"detail": "Email Varified Successfuly."})
            else:
                return Response({"detail": "Invalid or expired code."}, status=400)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=404)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVolunteerRole])
def get_volunteer_profile(request):

    try:
        volunteer = Volunteer.objects.select_related('user_id').get(
            user_id=request.user,
            status=VolunteerStatus.REGISTERED,
            user_id__is_active=True
        )
    except Volunteer.DoesNotExist:
        return Response({"error": "Volunteer is either inactive or not registered."}, status=403)

    serializer = Volunteerserializers(volunteer)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def change_volunteer_status(request, volunteer_id):
    status_choice = request.data.get('status')

    # Ensure valid status
    if status_choice not in VolunteerStatus.values:
        return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.status = status_choice
    volunteer.user_id.is_active= True
    volunteer.user_id.save()
    volunteer.save()

    serializer = Volunteerserializers(volunteer)
    return Response({'message': f'Volunteer status updated to {volunteer.status}.', 'data': serializer.data}, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])  # customize if needed
def assign_volunteer_to_patient(request):
    serializer = VolunteerAssignmentSerializer(data=request.data)
    if serializer.is_valid():
        volunteer = serializer.save()
        return Response({
            'message': 'Volunteer assigned successfully.',
            'volunteer_id': volunteer.id,
            'patient_id': volunteer.patient_id.id,
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsVolunteerRole])
def add_note(request):
    volunteer = Volunteer.objects.select_related('user_id', 'patient_id').get(user_id=request.user)

    if volunteer.status != VolunteerStatus.REGISTERED or not volunteer.user_id.is_active:
        return Response({"error": "Volunteer is not active or not registered."}, status=403)


    patient = volunteer.patient_id  # Already assigned in your model


    if not patient:
        return Response({"error": "No patient assigned to this volunteer."}, status=400)
    registed_patient_status = RegistrationPatientStatus.objects.filter(patientStatus__patient_id = patient)
 
    if not registed_patient_status or not patient.user_id.is_active:
        return Response({"error": "Assigned patient is not active or not registered."}, status=403)

    content = request.data.get('content')

    if not content:
        return Response({'error': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the note for the assigned patient
    note = Note.objects.create(
        patient_id=volunteer.patient_id,
        volunteer_id=volunteer,
        content=content
    )

    return Response({
        'message': 'Note added successfully.',
        'note': NoteSerializer(note).data
    }, status=status.HTTP_201_CREATED)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated , IsVolunteerRole])
# def add_note(request):
  
#     volunteer = Volunteer.objects.get(user_id=request.user)

#     # Check if volunteer is assigned to a patient
#     if not volunteer.patient_id:
#         return Response({'error': 'You are not assigned to any patient.'}, status=status.HTTP_400_BAD_REQUEST)

#     content = request.data.get('content')

#     if not content:
#         return Response({'error': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

#     # Create the note for the assigned patient
#     note = Note.objects.create(
#         patient_id=volunteer.patient_id,
#         volunteer_id=volunteer,
#         content=content
#     )

#     return Response({
#         'message': 'Note added successfully.',
#         'note': NoteSerializer(note).data
#     }, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole]) 
def list_all_notes(request):
    user = request.user

    # notes = Note.objects.select_related('patient_id', 'volunteer_id').all()
    notes = Note.objects.filter(
        patient_id__user_id__is_active=True,
        volunteer_id__user_id__is_active=True
)
    patient_id = request.query_params.get('patient_id', None)

    if user.role == Role.PATIENT:
        notes = notes.filter(patient_id__id=user.patient_user.id)

    elif user.role == Role.VOLUNTEE:
         notes = notes.filter(volunnteer_id__id=user.volunteer_user.id)

    else :
        if patient_id:
            notes = notes.filter(patient_id__id=patient_id)
    
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsVolunteerRole])
# def request_withdrawal(request):
#     volunteer = Volunteer.objects.get(user_id=request.user)

#     if volunteer.withdrawal_requested:
#         return Response({'error': 'Withdrawal request already submitted.'}, status=400)

#     serializer = WithdrawalRequestSerializer(data=request.data)
#     if serializer.is_valid():
#         volunteer.withdrawal_requested = True
#         volunteer.save()
#         return Response({'message': 'Withdrawal request submitted successfully.'})
#     return Response(serializer.errors, status=400)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsVolunteerRole ,IsPatientRole])
# def submit_withdrawal_request(request):
#     if IsVolunteerRole:
#         volunteer = Volunteer.objects.get(user_id=request.user)

#         if hasattr(volunteer, 'withdrawal_request'):
#             return Response({'error': 'You have already submitted a withdrawal request.'}, status=400)

#         serializer = WithdrawalRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             WithdrawalRequest.objects.create(
#                 user=volunteer,
#                 cause=serializer.validated_data['cause']
#             )
#             return Response({'message': 'Withdrawal request submitted successfully.'})
#     if IsPatientRole:
#         patient = Patient.objects.get(user_id=request.user)

#         if hasattr(patient, 'withdrawal_request'):
#             return Response({'error': 'You have already submitted a withdrawal request.'}, status=400)

#         serializer = WithdrawalRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             WithdrawalRequest.objects.create(
#                 user=patient,
#                 cause=serializer.validated_data['cause']
#             )
#             return Response({'message': 'Withdrawal request submitted successfully.'})
#     return Response(serializer.errors, status=400)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsVolunteerRole])
# def submit_withdrawal_request(request):
#     volunteer = Volunteer.objects.get(user_id=request.user)

#     if hasattr(volunteer, 'withdrawal_request'):
#         return Response({'error': 'You have already submitted a withdrawal request.'}, status=400)

#     serializer = WithdrawalRequestSerializer(data=request.data)
#     if serializer.is_valid():
#         WithdrawalRequest.objects.create(
#             user=volunteer,
#             cause=serializer.validated_data['cause']
#         )
#         return Response({'message': 'Withdrawal request submitted successfully.'})
    
#     return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_withdrawal_request(request):
    user = request.user

    if not hasattr(user, 'volunteer_user') and not hasattr(user, 'patient_user'):
        return Response({'error': 'Only volunteers or patients can submit withdrawal requests.'}, status=403)

    # Prevent duplicate request from same user
    if WithdrawalRequest.objects.filter(user=user ).exclude(status=WithdrawalrStatus.REJECTED).exists() :
        
        return Response({'error': 'You have already submitted a withdrawal request.'}, status=400)

    serializer = WithdrawalRequestSerializer(data=request.data)
    if serializer.is_valid():
        WithdrawalRequest.objects.create(
            user=user,
            cause=serializer.validated_data['cause']
        )
        return Response({'message': 'Withdrawal request submitted successfully.'})
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def list_withdrawal_requests(request):
    requests = WithdrawalRequest.objects.select_related('user').all()
    status = request.query_params.get('status', None)
    if status is not None:
        requests = requests.filter(status__icontains=status) 
    # if status == WithdrawalrStatus.PENDING:
    #     requests = requests.filter(status__icontains=status) 
    # if status == WithdrawalrStatus.APPROVED:
    #     requests = requests.filter(status__icontains=status) 
    # if status == WithdrawalrStatus.REJECTED:
    #     requests = requests.filter(status__icontains=status) 
        
    serializer = WithdrawalRequestSerializer(requests, many=True)
    return Response(serializer.data)


  

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def handle_withdrawal_request(request, request_id):
    try:
        withdrawal = WithdrawalRequest.objects.get(id=request_id)
    except WithdrawalRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=404)
    user = withdrawal.user
    original_email = user.email
    action = request.data.get('approve')
    if action is None:
        return Response({'error': 'Missing "approve" field (true/false)'}, status=400)

    withdrawal.is_approved = bool(action)
    withdrawal.status = WithdrawalrStatus.APPROVED
    withdrawal.save()

    if action:
        withdrawal.user.is_active = False
        withdrawal.user.email = original_email + "/deleted"
        withdrawal.user.username = withdrawal.user.email
        withdrawal.user.save()

        if user.role  == Role.VOLUNTEE:
            volunteer = user.volunteer_user  
            volunteer.status = VolunteerStatus.WITHDRAWN
            user.volunteer_user.staus =volunteer.status
            if volunteer.patient_id:
                volunteer.patient_id = None

            user.volunteer_user.save()
            try:
                send_mail(
                subject="Withdrawal Request Update",
                message=(f"Dear {user.first_name} {user.last_name},\n\n"
                    f"Your withdrawal request has been approved.\n"
                    f"Your account has been deactivated, and any assigned responsibilities have been cleared.\n\n"
                    f"If you have any questions or require further assistance, feel free to contact us.\n\n"
                    f"Best regards,\n"
                    f"The Support Team"
                ),
                from_email="alazem.noreply@gmail.com", 
                recipient_list=[original_email],
                fail_silently=False,
            )
            except :
                pass
                
            return Response({'message': 'Request approved. Volunteer deactivated. unassigned from patient'})
        
        if user.role == Role.PATIENT:
            patient_status = PatientStatus.objects.filter(patient_id__id = user.patient_user.id).first()
            registered_patient_status= patient_status.registration_statuses.first()
            if registered_patient_status is not None:
                registered_patient_status.delete()
                WithdrawalPatientStatus.objects.create(
                patientStatus=patient_status,
                date=timezone.now().date()
            )
        volunteer = user.patient_user.assigned_volunteer
        volunteer.patient_id = None
        volunteer.save()
        user.patient_user.save()
        patient_status.patient_id.user_id.save()

        try:
            send_mail(
                    subject="Withdrawal Request Update",
                    message=(f"Dear {user.first_name} {user.last_name},\n\n"
                        f"Your withdrawal request has been approved.\n"
                        f"Your account has been deactivated, and any assigned responsibilities have been cleared.\n\n"
                        f"If you have any questions or require further assistance, feel free to contact us.\n\n"
                        f"Best regards,\n"
                        f"The Support Team"
                    ),
                    from_email="alazem.noreply@gmail.com", 
                    recipient_list=[original_email],
                    fail_silently=False,
                )
        except:
            pass
        return Response({'message': 'Request approved. Patient deactivated. unassigned from volunteer'})

    else:
        try:
            send_mail(
                subject="Withdrawal Request Update",
                message=(
                    f"Dear {user.first_name} {user.last_name},\n\n"
                    f"Your withdrawal request has been reviewed and was not approved at this time.\n\n"
                    f"If you have any questions or would like to discuss this further, please don't hesitate to contact us.\n\n"
                    f"Best regards,\n"
                    f"The Support Team"
                ),
                from_email="alazem.noreply@gmail.com",
                recipient_list=[original_email],
                fail_silently=False,
            )
        except:
            pass
        return Response({'message': 'Request rejected Sucssefully.'})



@api_view(['GET'])
@permission_classes([IsAuthenticated , IsManagerRole])
def get_manager_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated , IsManagerRole])
def update_manager_profile(request):
    user = request.user

    # if user.role != Role.VOLUNTEE:
    #     return Response({'error': 'Only the Owner profile can update their profile.'}, status=status.HTTP_403_FORBIDDEN)

    # try:
    #     volunteer = Volunteer.objects.get(user_id=user)
    # except Volunteer.DoesNotExist:
    #     return Response({'error': 'Volunteer profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Update User fields
    user_fields = ['email' , 'first_name', 'last_name' , 'phone']
    for field in user_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()

    # Update Patient fields
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Your profile updated successfully.', 'data': serializer.data},
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

