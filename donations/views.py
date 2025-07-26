
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Donation, DonationStatus , DonationType, PatientDonation
from services.models import Patient
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from .serializers import  DonationSerializer, PatientDonationSerializer , AssociationDonationSerializer , varifySelectedPatientSerializeer
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from rest_framework.permissions import IsAuthenticated 
from ALAZEM.midlware.role_protection import IsAdminManagerRole
# from rest_framework import status
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.utils.timezone import now
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from .models import Donation

from donations import models

signer = Signer()

@api_view(['POST'])
def create_donations(request):
    donation_type =  request.data.get("donation_type")


        # Validate donation type
    if donation_type not in DonationType.values:
        return Response({'error': 'Invalid donation_type. Must be ASS or IND.'},
                        status=status.HTTP_400_BAD_REQUEST)

    if request.data.get("email") is None or request.data.get("email").strip()=="":
        return Response({'error' : 'the email fiels id required'})
    if donation_type == DonationType.ASSOCIATION:
        donation_data = {
            "email" : request.data.get("email"),
            "donation_type" : donation_type,
            "amount": request.data.get("amount"),
            "creation_date": timezone.now()
        }
        serializer = DonationSerializer(data=donation_data)
        if serializer.is_valid():
                donation = serializer.save()
                return Response({'message': 'Donation created successfully!', 'donation_id': str(donation.id)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    donations_input = request.data.get('donations')
    if not donations_input or not isinstance(donations_input, list):
        return Response({'error': 'donations must be a list of donation objects.'},
                        status=status.HTTP_400_BAD_REQUEST)

    total_amount = 0

    try:
        with transaction.atomic():
        # Validate all entries first without saving to avoid partial saves
            patients_to_donate = []
            # total_amount =0
            for entry in donations_input:
                id = entry.get('id')
                amount = entry.get('amount')

                # Validate required fields
                if not all([id, amount]):
                    return Response({'error': 'All fields (id, amount) are required for each donation.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Find the patient
                try:
                    patient_id = Patient.objects.get(
                       id = id
                        )
        
                    patient = Patient.objects.get(id=patient_id.id)
                except Patient.DoesNotExist:
                    return Response({'error': f'Patient with ID {patient_id} not found.'}, status=400)

                try:
                    amount_val = float(amount)
                    if amount_val <50:
                        return Response({'error': f'Invalid amount for patient {id}. Must be 50 at least.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except (ValueError, TypeError):
                    return Response({'error': f'Invalid amount format for patient {id}.'},
                                    status=status.HTTP_400_BAD_REQUEST)


                patients_to_donate.append({
                    'patient' : patient,
                    'amount': amount_val
                })
                total_amount += amount_val


            # All input validated, now create Donation once and PatientDonation entries
            donation = Donation.objects.create(
                email = request.data.get('email'),
                donation_type = donation_type,
                amount= total_amount,  # will update later
                creation_date=timezone.now()
            )
            
            
            for item in patients_to_donate:
                pd_data = {
                    'patient_id': item['patient'].id,
                    'donation_id': donation.id,
                    'amount': item['amount'],
                }    

                # Create PatientDonation instance
                pd_serializer = PatientDonationSerializer(data=pd_data)
                if pd_serializer.is_valid(raise_exception=True):
                    pd_serializer.save()
                else:
                    return Response(pd_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Update the Donation amount field to total sum

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': 'Donations created successfully!',
        'donation_type' : donation_type,
        'donation_id': donation.id,
        'total_amount': total_amount,
        'donations_created': len(donations_input)
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def varifySelectedPatient(request):
    try:
        patient_id = Patient.objects.get(
                            user_id__first_name = request.data.get('first_name') ,
                            user_id__last_name =request.data.get('last_name'),
                            father_name =  request.data.get('father_name'),
                            mother_name =  request.data.get('mother_name'),
                            )
    except Patient.DoesNotExist:
        return Response({'error': 'No matching patient found. Please check the provided information.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = varifySelectedPatientSerializeer(patient_id)
    return Response(serializer.data, status=status.HTTP_200_OK)               
  

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def get_donations(request):
    donations_list = Donation.objects.all()

    # Query params
    status_param = request.query_params.get('status_param', None)
    type_param = request.query_params.get('type_param', None)

    # Apply filters
    if status_param and status_param in DonationStatus.values:
        donations_list = donations_list.filter(donation_status=status_param)
 

    if type_param and type_param in DonationType.values:
        donations_list = donations_list.filter(donation_type=type_param)
  
#        return Response({'error': 'Invalid value'}, status=status.HTTP_400_BAD_REQUEST)
    donations_list = donations_list.order_by('-creation_date')

    serializer = DonationSerializer(donations_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminManagerRole])
def change_donation_status(request, donation_id):
    try:
        donation = Donation.objects.get(id=donation_id)
    except Donation.DoesNotExist:
        return Response({'error': 'Donation not found.'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('donation_status')

    if not new_status:
        return Response({'error': 'donation_status is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_status == DonationStatus.APPROVAL:
        session_url = create_checkout_session(request,donation)
        donation.donation_status = DonationStatus.APPROVAL
        donation.save()

       
        print(session_url.url)
        try:
            subject = "تم قبول تبرعك"
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
                <p>عزيزي/عزيزتي {donation.email}،</p>

                <p>يسعدنا إبلاغك بأن طلب التبرع الخاص بك قد تم قبوله.</p>
                <p><strong>المبلغ المطلوب سداده:</strong> ${donation.amount:.2f}</p>

                <p>يرجى اختيار طريقة الدفع المناسبة لك:</p>
                <ul>
                <li>💵 <strong>نقداً</strong>: يمكنك زيارة مكتبنا لإيداع المبلغ.</li>
                <li>💳 <strong>عبر الإنترنت (Stripe)</strong>: <a href="{session_url.url}" target="_blank">اضغط هنا للدفع الآمن عبر الإنترنت</a></li>
                </ul>

                <p>نشكر لك كرمك ودعمك لجمعية العزم لرعاية النساء المسنات من فاقدات البصر.</p>

                <p>مع أطيب التحيات،<br>
                جمعية العزم للكفيفات المسنات</p>
            </body>
            </html>
            """

            # نسخة نصية احتياطية للأنظمة التي لا تدعم HTML
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="alazem.noreply@gmail.com",
                recipient_list=[donation.email],
                html_message=html_message,
                fail_silently=False,
            )
        except:
            pass    
        return Response ({'message' : f"Thank you for your donation of ${donation.amount:.2f}."})
        

    elif new_status == DonationStatus.REJECTED:
        donation.donation_status = DonationStatus.REJECTED
        donation.save()

        try:
            subject = "حالة طلب التبرع الخاص بك"

            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
                <p>عزيزي/عزيزتي {donation.email}،</p>

                <p>نأسف لإبلاغك بأن طلب التبرع الخاص بك لم يتم قبوله في الوقت الحالي.</p>

                <p>نُعرب عن امتناننا العميق لرغبتك الصادقة في المساهمة، وندعوك للتواصل معنا في حال وجود أي استفسارات أو رغبتك في المحاولة مرة أخرى مستقبلاً.</p>

                <p>نشكر لك تفهمك واهتمامك.</p>

                <p>مع أطيب التحيات،<br>
                جمعية العزم للكفيفات المسنات</p>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="alazem.noreply@gmail.com",
                recipient_list=[donation.email],
                html_message=html_message,
                fail_silently=False,
            )
        except:
            pass
        return Response ({'message' : f"Soory, your donation request is rejected"})

    elif new_status == DonationStatus.COMPLETED:
        donation.donation_status = DonationStatus.COMPLETED
        donation.save()


        return Response ({'message' : f"Thank you for your donation of ${donation.amount:.2f}."})

    if new_status not in DonationStatus.values:
        return Response({'error': f'Invalid status. Must be one of: {list(DonationStatus.values)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    donation.donation_status = new_status
    donation.save()

    return Response({'message': 'Donation status updated successfully.', 'donation_id': donation.id,
                        'new_status': donation.donation_status}, status=status.HTTP_200_OK)


stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, donation):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Support for Blind Elderly Women ❤️',
                    'description': (
                        f"Thank you, {donation.email}, for spreading light and hope. "
                        "Your generous donation helps provide care, dignity, and support "
                        "to the amazing women at Al-Azm Association."
                    ),
                },
                'unit_amount': int(donation.amount * 100),  # amount in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/donation/success/'),
        cancel_url=request.build_absolute_uri('/donation/cancel/'),
        metadata={
            'donation_id': str(donation.id),
        },
        client_reference_id = donation.id
    )

    return session

@api_view(['POST'])
def complate_payment(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return Response({'error': '{e}'} , status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response({'error': '{e}'} , status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        donation_id = session.get('client_reference_id')
        print((donation_id))
        if donation_id:
            try:
                donation = Donation.objects.get(id=donation_id)
                donation.donation_status = DonationStatus.COMPLETED  # adjust field name accordingly
                donation.save()
            except Donation.DoesNotExist:
                return Response({'error': 'Donation not found'}, status=404)
            
        try:

            subject = "شكرًا لإتمام عملية التبرع"

            html_message = f"""
            <html lang="ar" dir="rtl">
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f9f9f9; padding: 20px;">
                <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ccc;">
                <p>عزيزي/عزيزتي <strong>{donation.email}</strong>،</p>

                <p>نتقدّم إليك بجزيل الشكر والامتنان على إتمام عملية التبرع بقيمة <strong>${donation.amount:.2f}</strong>.</p>

                <p>تبرعك الكريم يُسهم بشكل كبير في دعم أنشطتنا وخدمة النساء المسنات الكفيفات في جمعية العزم.</p>

                <p>نُثمّن عطائك ونعتبرك شريكًا في رسالتنا الإنسانية.</p>

                <p>مع خالص التقدير والاحترام،<br>
                جمعية العزم للمسنات الكفيفات</p>
                </div>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="alazem.noreply@gmail.com",
                recipient_list=[donation.email],
                html_message=html_message,
                fail_silently=False,
            )

        except:
            pass
    return Response({'message' : 'Complated' } , status=200) 