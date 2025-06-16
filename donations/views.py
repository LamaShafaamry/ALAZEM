# from .models import Donation 
# from services.models import Patient
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .serializers import DonationSerializer
# from rest_framework import status
# from django.utils import timezone
# from django.db import transaction


# @api_view(['POST'])
# def create_donations(request):
#     donations_input = request.data.get('donations')
#     if not donations_input or not isinstance(donations_input, list):
#         return Response({'error': 'donations must be a list of donation objects.'},
#                         status=status.HTTP_400_BAD_REQUEST)
#     total_amount = 0
#     created_donations = []
#     try:
#         with transaction.atomic():
#             for entry in donations_input:
#                 first_name = entry.get('first_name')
#                 last_name = entry.get('last_name')
#                 father_name = entry.get('father_name')
#                 amount = entry.get('amount')


#             for entry in donations_input:
#                 first_name = entry.get('first_name')
#                 last_name = entry.get('last_name')
#                 father_name = entry.get('father_name')
#                 amount = entry.get('amount')
#                 if (not first_name or not last_name or not  father_name or not  amount):
#                     return Response({'error': 'All fields (first_name, last_name, father_name, amount) are required for each donation.'},
#                                     status=status.HTTP_400_BAD_REQUEST)
#                 # Find the patient
#                 try:
#                     patient = Patient.objects.get(first_name=first_name, last_name=last_name, father_name=father_name)
#                 except Patient.DoesNotExist:
#                     return Response({'error': f'Patient not found: {first_name} {last_name} {father_name}'},
#                                     status=status.HTTP_400_BAD_REQUEST)
#                 # Prepare donation data
#                 donation_data = {
#                     'amount': amount,
#                     'patient': patient.id  # Assuming Donation has FK to Patient as 'patient'
#                 }
#                 serializer = DonationSerializer(data=donation_data)
#                 if serializer.is_valid():
#                     donation = serializer.save()
#                     created_donations.append(donation)
#                     total_amount += float(amount)
#                 else:
#                     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response({
#         'message': 'Donations created successfully!',
#         'total_amount': total_amount,
#         'donations_created': len(created_donations)
#     }, status=status.HTTP_201_CREATED)



# @api_view(['POST'])
# def create_donations(request):
#     donation_data = {
#         "amount": request.data.get("amount"),
#         #"creation_date": timezone.now()
#     }
    
#     serializer = DonationSerializer(data=donation_data)
#     if serializer.is_valid():
#             donation = serializer.save()
#             return Response({'message': 'Donation created successfully!', 'donation_id': str(donation.id)}, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from .models import Donation, PatientDonation
from services.models import Patient
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import DonationSerializer, PatientDonationSerializer , AssociationDonationSerializer
from rest_framework import status
from django.utils import timezone
from django.db import transaction

@api_view(['POST'])
def create_donations(request):
    # donationType_data = {
    #     "donation_type": request.data.get("donation_type")
    #     }
    donationType_data =  request.data.get("donation_type")
    if donationType_data == "ASS":
    
        donation_data = {
            "amount": request.data.get("amount"),
            "creation_date": timezone.now()
        }
        
        serializer = AssociationDonationSerializer(data=donation_data)
        if serializer.is_valid():
                donation = serializer.save()
                return Response({'message': 'Donation created successfully!', 'donation_id': str(donation.id)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        donations_input = request.data.get('donations')
        if not donations_input or not isinstance(donations_input, list):
            return Response({'error': 'donations must be a list of donation objects.'},
                            status=status.HTTP_400_BAD_REQUEST)

        total_amount = 0

        try:
            with transaction.atomic():
            # Validate all entries first without saving to avoid partial saves
                patients_to_donate = []
                total_amount =0
                for entry in donations_input:
                    first_name = entry.get('first_name')
                    last_name = entry.get('last_name')
                    father_name = entry.get('father_name')
                    amount = entry.get('amount')

                    # Validate required fields
                    if not all([first_name, last_name, father_name, amount]):
                        return Response({'error': 'All fields (first_name, last_name, father_name, amount) are required for each donation.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    # Find the patient
                    try:
                        patient = Patient.objects.get(first_name=first_name, last_name=last_name, father_name=father_name)
                    except Patient.DoesNotExist:
                        return Response({'error': f'Patient not found'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    # Validate amount can be converted to float
                    try:
                        amount_val = float(amount)
                        if amount_val <50:
                            return Response({'error': f'Invalid amount for patient {first_name} {last_name}. Must be 50 at least.'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except (ValueError, TypeError):
                        return Response({'error': f'Invalid amount format for patient {first_name} {last_name}.'},
                                        status=status.HTTP_400_BAD_REQUEST)


                    patients_to_donate.append({
                        'patient' : patient,
                        'amount': amount_val
                    })
                    total_amount += amount_val


                # All input validated, now create Donation once and PatientDonation entries
                donation = Donation.objects.create(
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
            'donation_id': donation.id,
            'total_amount': total_amount,
            'donations_created': len(donations_input)
        }, status=status.HTTP_201_CREATED)

