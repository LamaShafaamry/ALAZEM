from ALAZEM import settings
from .models import DeathPatientStatus, Patient , PatientStatus , PendingPatientStatus , Doctor , Appointment ,AppointmentStatus, RegistrationPatientStatus, TransitionPatientStatus
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from .serializers import PatientSerializer   , PendingPatientStatusSerializers , PatientStatusSerializers , DoctorSerializers , AppointmentSerializer , UpdatePatientSerializer
from users.serializers import UserSerializer
from django.contrib.auth.models import User 
from users.models import User , Role 
from rest_framework.permissions import IsAuthenticated 
from rest_framework.views import APIView
from ALAZEM.midlware.role_protection import IsDoctorRole , IsAdminManagerRole , IsPatientRole
from django.core.mail import send_mail



@api_view(['POST'])
def create_patient(request):
    patient_role = Role.PATIENT   

    if patient_role is None:
        return Response("{'error' : 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)} {patient_role}")

    if User.objects.filter(email=request.data.get('email')).exists():
        return Response("{'error' : 'A user with this email already exists.'}") 
    


    user = User.objects.create_user(
        username=request.data.get('email'),
        password=request.data.get('password'),
        email=request.data.get('email'),
        first_name= request.data.get("first_name"),
        last_name= request.data.get("last_name"),
        phone = request.data.get("phone"),
        role = patient_role,
        is_active = False

    )


    patient_data = {
        "first_name": request.data.get("first_name"),
        "last_name": request.data.get("last_name"),
        "father_name": request.data.get("father_name"),
        "mother_name": request.data.get("mother_name"),
        "date_of_birth": request.data.get("date_of_birth"),
        "place_of_birth": request.data.get("place_of_birth"),
        "nationality": request.data.get("nationality"),
        "national_ID": request.data.get("national_ID"),
        "family_book_number": request.data.get("family_book_number"),
        "disability_card_number": request.data.get("disability_card_number"),
        "certificate": request.data.get("certificate"),
        "other_disability": request.data.get("other_disability"),
        "history_of_blindness": request.data.get("history_of_blindness"),
        "cause": request.data.get("cause"),
        "chronic_illness": request.data.get("chronic_illness"),
        "requirement_of_ongoing_medication": request.data.get("requirement_of_ongoing_medication"),
        "requirement_of_special_care": request.data.get("requirement_of_special_care"),
        "user_id": user.id  # Associate the patient with the newly created user
    }

    # Deserialize the incoming JSON data
    serializer = PatientSerializer(data=patient_data)
    if serializer.is_valid():
        patient = serializer.save() 

        PatientStatus_data = {
            "patient_id" : patient.id
        }

        PatientStatusSerializer = PatientStatusSerializers(data=PatientStatus_data)
        if PatientStatusSerializer.is_valid():
            patientStatus = PatientStatusSerializer.save()

            PendingPatientStatus_data = {
            "patientStatus_id" : patientStatus.id,
            }

            PendingPatientStatusserializer = PendingPatientStatusSerializers(data=PendingPatientStatus_data)
            PendingPatientStatus.objects.create(patientStatus = patientStatus , date = timezone.now())

        return Response({'message': 'Patient created successfully!', 'patient_id': str(patient.id)}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_patient_profile(request):
    user = request.user

    if user.role != Role.PATIENT:
        return Response({'error': 'Only the Owner profile can update their profile.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        patient = Patient.objects.get(user_id=user)
    except Patient.DoesNotExist:
        return Response({'error': 'patient profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Update User fields
    user_fields = ['email' , 'first_name', 'last_name' , 'phone']
    for field in user_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()

    # Update Patient fields
    serializer = UpdatePatientSerializer(patient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Your profile updated successfully.', 'data': serializer.data},
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST','PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_doctor_profile(request):
    user = request.user

    if user.role != Role.DOCTOR:
        return Response({'error': 'Only the Owner profile can update their profile.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        doctor = Doctor.objects.get(user_id=user)
    except Doctor.DoesNotExist:
        return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Update User fields
    user_fields = ['email', 'first_name', 'last_name', 'phone']
    for field in user_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()

    # Update Doctor fields
    serializer = DoctorSerializers(doctor, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Your profile updated successfully.', 'data': serializer.data},
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 

@api_view(['POST'])
def create_doctor(request):
    # Check if the role "Doctor" exists
    doctor_role = Role.DOCTOR
    
    if doctor_role is None:
        return Response({'error': 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)

    if User.objects.filter(email=request.data.get('email')).exists():
        return Response("{'error' : 'A user with this email already exists.'}") 
    

    # Create the user
    user = User.objects.create_user(
        username=request.data.get('email'),
        password=request.data.get('password'),
        email=request.data.get('email', ''),  # Optional email field
        first_name=request.data.get("first_name"),
        last_name=request.data.get("last_name"),
        phone=request.data.get("phone"),
        role=doctor_role
    )

    # Prepare doctor data
    doctor_data = {
        "first_name": request.data.get('first_name'),  
        "last_name": request.data.get('last_name'),
        "speciality": request.data.get('speciality'),
        "user_id": user.id,
    }

    # Validate and save doctor data
    serializer = DoctorSerializers(data=doctor_data)
    if serializer.is_valid():
        doctor = serializer.save()
        return Response({'message': 'Doctor created successfully!', 'doctor_id': str(doctor.id)}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_patients(request):
    patients_list = Patient.objects.all()
    name = request.query_params.get('name', None)
    status_filter = request.query_params.get('status_filter' , None)  # 'pending' or 'registered'
    is_active = request.query_params.get('is_active' , None)

    if name:
        patients_list = patients_list.filter(first_name__icontains=name) | patients_list.filter(last_name__icontains=name)
    # serializer = PatientSerializer(patients_list, many=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)


    if status_filter == 'pending':
        patients_list = patients_list.filter(
            patientstatus__pending_statuses__isnull=False
        ).distinct()
    elif status_filter == 'registered':
        patients_list = patients_list.filter(
            patientstatus__registration_statuses__isnull=False
        ).distinct()
    elif status_filter == 'death':
        patients_list = patients_list.filter(
            patientstatus__death_statuses__isnull=False
        ).distinct()
    elif status_filter == 'transition':
        patients_list = patients_list.filter(
            patientstatus__transition_statuses__isnull=False
        ).distinct()
          
    else :
        return Response({'message': 'Unvalid status search!  Use "pending" or "registered" , or "death" or "transition"'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = PatientSerializer(patients_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_doctors(request):
    doctors_list = Doctor.objects.all()
    name = request.query_params.get('name', None)
    speciality = request.query_params.get('speciality' , None)

    if name:
        doctors_list = doctors_list.filter(first_name__icontains=name) | doctors_list.filter(last_name__icontains=name) 
    if speciality:
        doctors_list = doctors_list.filter(speciality__icontains=speciality)
        
    serializer = DoctorSerializers(doctors_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

    

@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_users(request):
    users_list = User.objects.all()
    name = request.query_params.get('name', None)
    role = request.query_params.get('role', None)
    email = request.query_params.get('email', None)

    if name:
        users_list = users_list.filter(first_name__icontains=name) | users_list.filter(last_name__icontains=name) 
    if role:
        users_list =  users_list.filter(role__icontains=role) 
    if email :
        users_list =users_list.filter(email__icontains=email)
    serializer = UserSerializer(users_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def change_patient_status(request,patient_id):
 
    patient_status = PatientStatus.objects.filter(patient_id__id = patient_id).first()
    pendig_patient_status= patient_status.pending_statuses.first()
    if pendig_patient_status is None:
        return Response({'error': 'Pending Patient status not found.'}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')  # 'approve' or 'reject'

    if action == 'approve':
        # Create RegistrationPatientStatus
        RegistrationPatientStatus.objects.create(
            patientStatus=patient_status,
            date=timezone.now().date()
        )

        patient_status.patient_id.user_id.is_active =  True
        patient_status.patient_id.user_id.save()
        pendig_patient_status.delete()
        return Response({'message': 'Patient approved and registered.'}, status=status.HTTP_200_OK)
    
    elif action == 'transition':
        TransitionPatientStatus.objects.create(
            patientStatus=patient_status,
            date=timezone.now().date()
        )

        patient_status.patient_id.user_id.is_active =  False
        patient_status.patient_id.user_id.save()
        pendig_patient_status.delete()
        return Response({'message': 'Patient approved and registered.'}, status=status.HTTP_200_OK)

    elif action == 'death':
        DeathPatientStatus.objects.create(
            patientStatus=patient_status,
            date=timezone.now().date()
        )

        patient_status.patient_id.user_id.is_active =  False
        patient_status.patient_id.user_id.save()
        pendig_patient_status.delete()
        return Response({'message': 'Patient approved and registered.'}, status=status.HTTP_200_OK)

    elif action == 'reject':
        pendig_patient_status.delete()
        return Response({'message': 'Patient application rejected.'}, status=status.HTTP_200_OK)

    else:
        return Response({'error': 'Invalid action. Use "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated ,IsAdminManagerRole ])
def create_appointment(request):
    appointment_data ={
        "patient_id" : request.data.get('patient_id'),
        "doctor_id" : request.data.get('doctor_id'),
        "appointment_date" : request.data.get('appointment_date'),
        "medical_report" : "",

    }
    serializer = AppointmentSerializer(data=appointment_data)
    if serializer.is_valid():
        patient_id = serializer.validated_data['patient_id']
        doctor_id = serializer.validated_data['doctor_id']
        appointment_date = serializer.validated_data['appointment_date']

        appointment_date = appointment_date.date()


        if Appointment.objects.filter(doctor_id=doctor_id, appointment_date__date=appointment_date).exists():
            return Response({'error': 'The doctor already has an appointment at this time.'}, status=status.HTTP_400_BAD_REQUEST)
        if Appointment.objects.filter(patient_id=patient_id, appointment_date__date=appointment_date).exists():
            return Response({'error': 'The patent already has an appointment at this time.'}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment = serializer.save()
        return Response({'message': 'Appointment created successfully!', 'appointment_id': appointment.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctorRole])
def update_appointment_status(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')

    if action not in ['approve', 'reject']:
        return Response({'error': 'Invalid action. Must be "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)

    if action == 'approve':
        appointment.appointment_status = AppointmentStatus.APPROVAL
        appointment.approved_date = timezone.now()
        appointment.save()
        return Response({'message': 'Appointment approved.', 'appointment_id': appointment.id}, status=status.HTTP_200_OK)
    
    else:  # reject
        appointment.appointment_status = AppointmentStatus.REJECTED
        appointment.save()

        # manager_email = "manager@example.com"  # or fetch dynamically
        # send_mail(
        #     subject="Appointment Rejected",
        #     message=f"Appointment {appointment.id} for patient {appointment.patient_id} has been rejected by the doctor.",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[manager_email],
        #     fail_silently=True,
        # )

        return Response({'message': 'Appointment rejected.', 'appointment_id': appointment.id}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctorRole])
def update_medical_report(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if appointment.appointment_status != AppointmentStatus.APPROVAL:
        return Response({'error': 'Medical report can only be updated for approved appointments.'}, status=status.HTTP_400_BAD_REQUEST)


    medical_report = request.data.get('medical_report')
    if medical_report is None:
        return Response({'error': 'Medical report is required.'}, status=status.HTTP_400_BAD_REQUEST)

    appointment.medical_report = medical_report
    appointment.save()

    return Response({'message': 'Medical report updated.', 'appointment_id': appointment.id}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctorRole])
def doctor_appointments(request):
    doctor = request.user.doctor  # Assumes the logged-in user is linked to a Doctor model
    appointments = Appointment.objects.filter(doctor_id=doctor).order_by('-appointment_date')

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatientRole])
def patient_approved_appointments(request):
    try:
        patient = request.user.patient  # Assumes User has OneToOne with Patient
    except AttributeError:
        return Response({'error': 'User is not linked to a patient.'}, status=status.HTTP_400_BAD_REQUEST)

    # Start with approved appointments
    approved_appointments = Appointment.objects.filter(
        patient_id=patient,
        appointment_status=AppointmentStatus.APPROVAL
    ).order_by('-appointment_date')

    # Optional filter for completion status
    completed_filter = request.query_params.get('completed', None)

    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            approved_appointments = approved_appointments.exclude(medical_report__isnull=True).exclude(medical_report__exact="")
        elif completed_filter.lower() == 'false':
            approved_appointments = approved_appointments.filter(medical_report__isnull=True) | approved_appointments.filter(medical_report__exact="")

    serialized = AppointmentSerializer(approved_appointments, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def get_all_appointments(request):
    appointments = Appointment.objects.all().order_by('-appointment_date')

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
