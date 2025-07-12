
from django.shortcuts import get_object_or_404
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
from rest_framework import status
from django.core.mail import send_mail

from donations import models



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
                # except Patient.DoesNotExist:
                #     return Response({'error': f'Patient {id} not found.'}, status=400)
                # except Patient.MultipleObjectsReturned:
                #     return Response({'error': f'Multiple patients matched {first_name} {last_name}. Refine your input.'}, status=400)

                # if not patient_id:
                #     return Response({'error': 'patient_id is required for each donation entry.'}, status=400)

                # try:
                    patient = Patient.objects.get(id=patient_id.id)
                except Patient.DoesNotExist:
                    return Response({'error': f'Patient with ID {patient_id} not found.'}, status=400)

                # try:
                #     patient = Patient.objects.get('user_id__id')
                # except Patient.DoesNotExist:
                #     return Response({'error': f'{first_name} {last_name} Patient not found'},
                #                     status=status.HTTP_400_BAD_REQUEST)

                # Validate amount can be converted to float
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
  

# @api_view(['GET'])
# @permission_classes([IsAuthenticated , IsAdminManagerRole])
# def get_donations(request):
        
#     donations_list= Donation.objects.all()
#     donation_status = request.query_params.get('donation_status',None)
#     type = request.query_params.get('type' , None)
    
#     if donation_status and donation_status in DonationStatus.values:
#         donations_list = donations_list.filter(donation_status=donation_status)
#     elif type and type in DonationType.values:
#         donations_list = donations_list.filter(donation_type__icontains=type)

    
#     donations_list = donations_list.order_by('-creation_date') 

#     serializer = DonationSerializer(donations_list, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


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
        donation.donation_status = DonationStatus.APPROVAL
        donation.save()
        if donation.donation_type == DonationType.ASSOCIATION:
            return Response ({'message' : f"Thank you for your donation of ${donation.amount:.2f}."})
        
        if donation.donation_type == DonationType.INDIVIDUAL:
            patient_donations = PatientDonation.objects.filter(donation_id=donation)
            total_amount = patient_donations.aggregate(total=models.Sum('amount'))['total'] or 0

            return Response({'message' : f"Thank you for your donation. The total amount assigned to patients is ${total_amount:.2f}."}) 
        # else:
        #     message = "Thank you for your donation."

        # send_donation_email(
        #     to_email=donation.email,
        #     subject="Donation Approved",
        #     message=message
        # )

    if new_status not in DonationStatus.values:
        return Response({'error': f'Invalid status. Must be one of: {list(DonationStatus.values)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    donation.donation_status = new_status
    donation.save()

    return Response({'message': 'Donation status updated successfully.', 'donation_id': donation.id,
                     'new_status': donation.donation_status}, status=status.HTTP_200_OK)
