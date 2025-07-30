import base64
from datetime import timedelta
import time
import hashlib
import hmac
import os
import random
import django
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from ALAZEM import settings
from donations.models import DonationStatus, PatientDonation
from donations.serializers import PatientDonationSerializer
from .models import DeathPatientStatus, DoctorStatus, Patient , PatientStatus , PendingPatientStatus , Doctor , Appointment ,AppointmentStatus, RegistrationPatientStatus, RejectedPatientStatus , WithdrawalPatientStatus
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
from ALAZEM.midlware.role_protection import IsDoctorRole , IsAdminManagerRole , IsPatientRole, IsVolunteerRole
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags

from django.db.models import Q


@api_view(['POST'])
def create_patient(request):
    patient_role = Role.PATIENT   

    if patient_role is None:
        return Response("{'error' : 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)} {patient_role}")

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
        role = patient_role,
        is_active = False,
        is_email_varification = False


    )


    patient_data = {
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

        user = User.objects.get(email=user.email)
        varification_code = f"{random.randint(100000, 999999)}"
        user.varification_code = varification_code
        user.save()

        serializer.save() 
        try:

            subject = "رمز التحقق من الحساب"

            html_message = f"""
            <html lang="ar" dir="rtl">
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f9f9f9; padding: 20px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ddd;">
                <p>مرحبًا <strong>{user.first_name} {user.last_name}</strong>،</p>

                <p>رمز التحقق الخاص بك هو:</p>

                <div style="font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px 0; text-align: center;">
                    {varification_code}
                </div>

                <p>يرجى إدخال هذا الرمز لإكمال عملية التحقق من الحساب.</p>

                <p>مع أطيب التحيات،<br>
                 جمعية العزم للكفيفات المسنات</p>
                </div>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="alazem.noreply@gmail.com",
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

        except:
            pass
        return Response({'message': 'Patient created successfully!'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatientRole])
def get_patient_profile(request):

    try:
        patient = Patient.objects.select_related('user_id').get(
            user_id=request.user,
            user_id__is_active=True
        )
    except Patient.DoesNotExist:
        return Response({"error": "Patient is either inactive or not registered."}, status=403)

    serializer = PatientSerializer(patient)
    return Response(serializer.data)


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
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def create_doctor(request):
    doctor_role = Role.DOCTOR
    
    if doctor_role is None:
        return Response({'error': 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)

    if User.objects.filter(email=request.data.get('email')).exists():
        return Response("{'error' : 'A user with this email already exists.'}") 
    

    # Create the user
    user = User.objects.create_user(
        username=request.data.get('email'),
        email=request.data.get('email', ''),  # Optional email field
        first_name=request.data.get("first_name"),
        last_name=request.data.get("last_name"),
        phone=request.data.get("phone"),
        role=doctor_role
    )

    # Prepare doctor data
    doctor_data = {
        "speciality": request.data.get('speciality'),
        "user_id": user.id,
    }

    # Validate and save doctor data
    serializer = DoctorSerializers(data=doctor_data)
    if serializer.is_valid():
        doctor = serializer.save()
        
        token = generate_token(user.id)
        print(token)
        subject = "تفعيل حسابك في نظام العيادة"

        reset_link = f"http://127.0.0.1:8000/users/auth/reset-password?token={token}"  # Replace with your actual reset link logic

        html_message = f"""
        <html lang="ar" dir="rtl">
        <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ddd;">
                <h2 style="color: #333;">مرحبًا دكتور {doctor.user_id.first_name} {doctor.user_id.last_name}،</h2>

                <p>تم إنشاء حسابك بنجاح في نظام العيادة من قبل الإدارة.</p>

                <p>قبل أن تتمكن من تسجيل الدخول، يجب عليك تعيين كلمة مرور جديدة باستخدام الرابط التالي:</p>

                <p style="margin: 20px 0;">
                    <a href="{reset_link}" style="display: inline-block; background-color: #2b8a3e; color: white; padding: 12px 20px; border-radius: 6px; text-decoration: none;">
                        تعيين كلمة المرور
                    </a>
                </p>

                <p>هذا الرابط صالح لفترة محدودة. إذا لم تطلب هذا البريد، يرجى تجاهله.</p>

                <p>مع خالص التقدير،<br>
                فريق الدعم - جمعية العزم للكفيفات المسنات</p>
            </div>
        </body>
        </html>
        """

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email="alazem.noreply@gmail.com",
            recipient_list=[doctor.user_id.email],
            html_message=html_message,
            fail_silently=False,
        )

        return Response({'message': 'Doctor created successfully!', 'doctor_id': str(doctor.id)}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_token(user_id: int) -> str:
    timestamp = int(time.time())
    data = f"{user_id}:{timestamp}".encode("utf-8")  # ✅ text part
    signature = hmac.new(settings.SECRET_KEY.encode(), data, hashlib.sha256).digest()
    payload = base64.urlsafe_b64encode(data).decode()  # 🔐 encode data separately
    sig = base64.urlsafe_b64encode(signature).decode()
    return f"{payload}.{sig}"

def verify_token(token: str, max_age: int = 3600) -> int | None:
    try:
        if '.' not in token:
            raise ValueError("Token format invalid")

        payload_b64, sig_b64 = token.split(".")

        data = base64.urlsafe_b64decode(payload_b64.encode())
        signature = base64.urlsafe_b64decode(sig_b64.encode())

        # 🧠 Decode safely now — only UTF-8 data here
        user_id_str, timestamp_str = data.decode("utf-8").split(":")
        timestamp = int(timestamp_str)

        # # ⏳ Expiration check
        # if int(time.time()) - timestamp > max_age:
        #     raise ValueError("Token expired")

        # 🔁 Validate signature
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), data, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Invalid signature")

        return int(user_id_str)
    except Exception as e:
        print(f"[verify_token] Error: {e}")
        return None

@api_view(['POST'])
def registration_doctor(request):
    if User.objects.filter(email=request.data.get('email')).exists():
        return Response("{'error' : 'A user with this email already exists.'}") 
    
    if request.data.get('password') is None:
        return Response({'error' : 'Passwoard is requied' },status=status.HTTP_400_BAD_REQUEST ) 
    try:
        validate_password(request.data.get("password"))  # Optional: pass user=User instance if needed
    except ValidationError as e:
            return Response(
                {"errors": e.messages},  # Returns a list of validation messages
                status=status.HTTP_400_BAD_REQUEST
            )
    

    # Create the user
    user = User.objects.create_user(
        username=request.data.get('email'),
        email=request.data.get('email'),  # Optional email field
        password=request.data.get('password'),
        first_name=request.data.get("first_name"),
        last_name=request.data.get("last_name"),
        phone=request.data.get("phone"),
        role=Role.DOCTOR,
        is_active = False,
        is_email_varification = False
    )

    # Prepare doctor data
    doctor_data = {
        "speciality": request.data.get('speciality'),
        "user_id": user.id,
    }

    # Validate and save doctor data
    serializer = DoctorSerializers(data=doctor_data)
    if serializer.is_valid():
        user = User.objects.get(email=user.email)
        varification_code = f"{random.randint(100000, 999999)}"
        user.varification_code = varification_code
        user.save()
        doctor = serializer.save()  # Save the patient using the serializer
        
        try:
            send_mail(
                        subject="Your Password Reset Verification Code",
                        message=f"Hello {user.username},\n\nYour password reset verification code is: {varification_code}\n\n",
                        from_email="alazem.noreply@gmail.com", 
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
        except:
            pass
        return Response({'message': 'Doctor created successfully!', 'doctor_id': str(doctor.id)}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def change_doctor_status(request, doctor_id):
    status_choice = request.data.get('status')

    if status_choice not in DoctorStatus.values:
        return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, id=doctor_id)
    if status_choice == DonationStatus.APPROVAL:
        doctor.user_id.is_active= True

    doctor.doctor_status = status_choice
    doctor.user_id.save()
    doctor.save()

    serializer = DoctorSerializers(doctor)
    return Response({'message': f'Doctor status updated to {doctor.doctor_status}.', 'data': serializer.data}, status=status.HTTP_200_OK)



@api_view(['POST'])
def set_doctor_password(request):
    token = request.data.get('token')
    user_id = verify_token(token)
    if user_id is None:
        return Response({'error' : 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    print(user_id)
    user =User.objects.get(id=user_id) 
    new_password = request.data.get('new_password')
    user.set_password(new_password)
    user.save()
    return Response({"detail": "Password has been reset."})
          

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctorRole])
def get_doctor_profile(request):

    try:
        doctor = Doctor.objects.select_related('user_id').get(
            user_id=request.user,
            user_id__is_active=True
        )
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor is either inactive or not registered."}, status=403)

    serializer = DoctorSerializers(doctor)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_patients(request):
    patients_list = Patient.objects.filter(user_id__is_email_varification = True)
    name = request.query_params.get('name', None)
    status_filter = request.query_params.get('status_filter' , None)  

    if name:
        patients_list = patients_list.filter(first_name__icontains=name) | patients_list.filter(last_name__icontains=name)
    # serializer = PatientSerializer(patients_list, many=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)


    if status_filter == 'pending':
        patients_list = patients_list.filter(
            patient_status__pending_statuses__isnull=False
        ).distinct()
    elif status_filter == 'registered':
        patients_list = patients_list.filter(
            patient_status__registration_statuses__isnull=False
        ).distinct()
    elif status_filter == 'death':
        patients_list = patients_list.filter(
            patient_status__death_statuses__isnull=False
        ).distinct()
    elif status_filter == 'withdrawal':
        patients_list = patients_list.filter(
            patient_status__withdrawal_statuses__isnull=False
        ).distinct()
          
    else :
        return Response({'message': 'Unvalid status search!  Use "pending" or "registered" , or "death" or "withdrawal"'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = PatientSerializer(patients_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_doctors(request):
    doctors_list = Doctor.objects.all()
    name = request.query_params.get('name', None)
    speciality = request.query_params.get('speciality' , None)
    doctor_status = request.query_params.get('status' , None)
    if name:
        doctors_list = doctors_list.filter(first_name__icontains=name) | doctors_list.filter(last_name__icontains=name) 
    if speciality:
        doctors_list = doctors_list.filter(speciality__icontains=speciality)
    if doctor_status:
        doctors_list = doctors_list.filter(doctor_status__icontains=doctor_status)
               
    serializer = DoctorSerializers(doctors_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

    

@api_view(['GET'])
@permission_classes([IsAuthenticated , IsAdminManagerRole])
def get_users(request):
    users_list = User.objects.exclude(email__icontains="deleted").order_by('-id')
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
    try:
        patient = Patient.objects.get(id = patient_id)
    except:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
   
    action = request.data.get('action')  # 'approve' or 'reject'

    if action == 'approve':
        patient_status = PatientStatus.objects.filter(patient_id__id = patient_id).first()
        pendig_patient_status= patient_status.pending_statuses.first()
        if pendig_patient_status is None:
            return Response({'error': 'Pending Patient status not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create RegistrationPatientStatus
        RegistrationPatientStatus.objects.create(
            patientStatus=patient_status,
            date=timezone.now()
        )

        patient_status.patient_id.user_id.is_active =  True
        patient_status.patient_id.user_id.save()
        pendig_patient_status.delete()
        try:

            subject = "تحديث حالة طلب التسجيل"

            html_message = f"""
            <html lang="ar" dir="rtl">
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f7f7f7; padding: 20px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ccc;">
                <p>مرحبًا <strong>{patient.user_id.first_name} {patient.user_id.last_name}</strong>،</p>

                <p>يسعدنا إبلاغك بأنه قد تمت الموافقة على طلب التسجيل الخاص بك، وتم تفعيل حسابك بنجاح.</p>

                <p>في حال كان لديك أي استفسارات أو تحتاج إلى أي مساعدة إضافية، لا تتردد في التواصل معنا.</p>

                <p>مع أطيب التحيات،<br>
                فريق الدعم</p>
                </div>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="alazem.noreply@gmail.com",
                recipient_list=[patient.user_id.email],
                html_message=html_message,
                fail_silently=False,
            )

        except:
            pass
        return Response({'message': 'Patient approved and registered.'}, status=status.HTTP_200_OK)
    
    elif action == 'death':
        patient_status = PatientStatus.objects.filter(patient_id__id = patient_id).first()
        register_patient_status= patient_status.registration_statuses.first()
        if register_patient_status is None:
            return Response({'error': 'Register Patient status not found.'}, status=status.HTTP_404_NOT_FOUND)

        DeathPatientStatus.objects.create(
            patientStatus=patient_status,
            date=timezone.now()
        )

        patient_status.patient_id.user_id.is_active =  False
        patient_status.patient_id.user_id.save()
        register_patient_status.delete()
 
    elif action == 'reject':
        patient_status = PatientStatus.objects.filter(patient_id__id = patient_id).first()
        pendig_patient_status= patient_status.pending_statuses.first()
        if pendig_patient_status is None:
            return Response({'error': 'Pending Patient status not found.'}, status=status.HTTP_404_NOT_FOUND)

        RejectedPatientStatus.objects.create(
            patientStatus=patient_status,
            date=timezone.now()
        )

        patient_status.patient_id.user_id.is_active =  False
        patient_status.patient_id.user_id.save()
        pendig_patient_status.delete()
 
        try:

            subject = "تحديث حالة طلب التسجيل"

            html_message = f"""
            <html lang="ar" dir="rtl">
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f9f9f9; padding: 20px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ccc;">
                <p>عزيزي/عزيزتي <strong>{patient.user_id.first_name} {patient.user_id.last_name}</strong>،</p>

                <p>نأسف لإبلاغك بأن طلب التسجيل الخاص بك لم يتم قبوله في الوقت الحالي.</p>

                <p>نقدّر اهتمامك ورغبتك في الانضمام، ونرحب بك للتقديم مرة أخرى مستقبلًا.</p>

                <p>إذا كان لديك أي استفسار أو تحتاج إلى توضيحات إضافية، لا تتردد في التواصل معنا.</p>

                <p>مع خالص التقدير،<br>
                فريق الدعم</p>
                </div>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="alazem.noreply@gmail.com",
                recipient_list=[patient.user_id.email],
                html_message=html_message,
                fail_silently=False,
            )
        except:
            pass
        return Response({'message': 'Patient Rejected.'}, status=status.HTTP_200_OK)

    elif action == 'reject':
        pendig_patient_status.delete()
        return Response({'message': 'Patient application rejected.'}, status=status.HTTP_200_OK)

    else:
        return Response({'error': 'Invalid action. Use "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated ,IsAdminManagerRole ])
def create_appointment(request):

    APPOINTMENT_DURATION =timedelta(minutes=60) 

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
        appointment_end = appointment_date + APPOINTMENT_DURATION

     # Check for overlapping appointments for the same doctor
        conflicting_appointments = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date__lt= appointment_end,
            appointment_date__gt= appointment_date - APPOINTMENT_DURATION
        )

        conflicting_patientappointments = Appointment.objects.filter(
            patient_id=patient_id,
            appointment_date__lt=appointment_end,
            appointment_date__gt=appointment_date - APPOINTMENT_DURATION
        )
        if conflicting_appointments.exists():
            return Response(
                {'error': 'The doctor already has an appointment during this time slot.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if conflicting_patientappointments.exists():
            return Response(
                {'error': 'The patient already has an appointment during this time slot.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # if Appointment.objects.filter(doctor_id=doctor_id, appointment_date__date=appointment_date).exists():
        #     return Response({'error': 'The doctor already has an appointment at this time.'}, status=status.HTTP_400_BAD_REQUEST)
        # if Appointment.objects.filter(patient_id=patient_id, appointment_date__date=appointment_date).exists():
        #     return Response({'error': 'The patent already has an appointment at this time.'}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment = serializer.save()

        # subject = "تحديث حالة طلب التسجيل"

        # html_message = f"""
        # <html lang="ar" dir="rtl">
        # <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f9f9f9; padding: 20px;">
        #     <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ccc;">
        #     <p>عزيزي/عزيزتي <strong>{doctor.user_id.first_name} {patient.user_id.last_name}</strong>،</p>

        #     <p>نأسف لإبلاغك بأن طلب التسجيل الخاص بك لم يتم قبوله في الوقت الحالي.</p>

        #     <p>نقدّر اهتمامك ورغبتك في الانضمام، ونرحب بك للتقديم مرة أخرى مستقبلًا.</p>

        #     <p>إذا كان لديك أي استفسار أو تحتاج إلى توضيحات إضافية، لا تتردد في التواصل معنا.</p>

        #     <p>مع خالص التقدير،<br>
        #     فريق الدعم</p>
        #     </div>
        # </body>
        # </html>
        # """

        # plain_message = strip_tags(html_message)

        # send_mail(
        #     subject=subject,
        #     message=plain_message,
        #     from_email="alazem.noreply@gmail.com",
        #     recipient_list=[patient.user_id.email],
        #     html_message=html_message,
        #     fail_silently=False,
        # )

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
    appointments = Appointment.objects.filter(doctor_id=doctor).order_by('-id')

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatientRole])
def get_patient_appointments(request):
    try:
        patient = request.user.patient_user  # Assumes User has OneToOne with Patient
    except AttributeError:
        return Response({'error': 'User is not linked to a doctor.'}, status=status.HTTP_400_BAD_REQUEST)

    # appointments_list = Appointment.objects.filter(patient_id = patient.id, appointment_status = AppointmentStatus.APPROVAL  appointment_status =AppointmentStatus.REJECT).order_by('-appointment_date')
    appointments_list = Appointment.objects.filter(
    patient_id=patient.id,
).order_by('-id')
    
    appointments_list = appointments_list.filter(    Q(appointment_status=AppointmentStatus.APPROVAL) | Q(appointment_status=AppointmentStatus.CANCELED)
)
    # Start with approved appointments
    status_param = request.query_params.get('status_param', None)

    # Apply filters
    if status_param and status_param in AppointmentStatus.values:
        appointments_list = appointments_list.filter(appointment_status=status_param)
 

    # Optional filter for completion status
    completed_filter = request.query_params.get('completed', None)

    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            appointments_list = appointments_list.exclude(medical_report__isnull=True).exclude(medical_report__exact="")
        elif completed_filter.lower() == 'false':
            appointments_list = appointments_list.filter(medical_report__isnull=True) | appointments_list.filter(medical_report__exact="")

    serialized = AppointmentSerializer(appointments_list, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatientRole])
def cancel_appointments(request , appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    if appointment.patient_id.user_id != request.user:
        return Response({'error': 'You are not allowed to cancel this appointment.'}, status=status.HTTP_403_FORBIDDEN)

    if appointment.appointment_status == AppointmentStatus.APPROVAL:

        appointment.appointment_status = AppointmentStatus.CANCELED
        appointment.approved_date = timezone.now()
        appointment.save()


        subject = "إلغاء الموعد من قبل المريض"

        # Build HTML message
        html_message = f"""
        <html lang="ar" dir="rtl">
        <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f9f9f9; padding: 20px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ccc;">
                <p>عزيزي/عزيزتي <strong>{appointment.doctor_id.user_id.first_name} {appointment.doctor_id.user_id.last_name}</strong>،</p>

                <p>نود إعلامك بأن المريضة <strong>{appointment.patient_id.user_id.first_name} {appointment.patient_id.user_id.last_name}</strong> قد قامت بإلغاء موعدها المحدد بتاريخ <strong>{appointment.appointment_date}</strong>.</p>

                <p>نرجو أخذ العلم بهذا التغيير، وإذا كنت بحاجة إلى تحديث الجدول الزمني ، يمكنك التواصل مع الجمعية.</p>

                <p>مع خالص التقدير،<br>
                جمعية العزم للكفيفات المسنات</p>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        plain_message = strip_tags(html_message)

        # Recipients: doctor and manager
        recipients = [
            appointment.doctor_id.user_id.email,
            # appointment.manager_id.user_id.email  # Assuming this exists in your model
        ]

        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email="alazem.noreply@gmail.com",
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )

        serializer = AppointmentSerializer(appointment)
        return Response({
            'message': 'Appointment rejected.',
            'appointment': serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
                'error': "You can't rejected this appointment.",
            }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def get_all_appointments(request):
    appointments = Appointment.objects.all().order_by('-appointment_date')
    doctor_id = request.query_params.get('doctor_id', None)
    patient_id = request.query_params.get('patient_id', None)
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)
    if patient_id:
        appointments = appointments.filter(patient_id=patient_id)
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatientRole])
def get_my_donations(request):
    try:
        patient = request.user.patient_user  # Assumes User has OneToOne with Patient
    except AttributeError:
        return Response({'error': 'User is not linked to a patient.'}, status=status.HTTP_400_BAD_REQUEST)

    # Start with approved appointments
    completed_donation = PatientDonation.objects.filter(
        patient_id=patient,
        donation_id__donation_status=DonationStatus.COMPLETED
    ).order_by('-donation_id__creation_date')

    # Optional filter for completion status
    # completed_filter = request.query_params.get('completed', None)

    # if completed_filter is not None:
    #     if completed_filter.lower() == 'true':
    #         approved_appointments = approved_appointments.exclude(medical_report__isnull=True).exclude(medical_report__exact="")
    #     elif completed_filter.lower() == 'false':
    #         approved_appointments = approved_appointments.filter(medical_report__isnull=True) | approved_appointments.filter(medical_report__exact="")

    serialized = PatientDonationSerializer(completed_donation, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)
