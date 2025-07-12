from rest_framework import serializers
from .models import Donation, PatientDonation
from services.models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'father_name'
            
        ]



class AssociationDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            'email',
            'donation_type',
            'donation_status',
            'amount',
            'creation_date'
        ]


class DonationSerializer(serializers.ModelSerializer):
    patients = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            'id',
            'email',
            'donation_type',
            'donation_status',
            'amount',
            'creation_date',
            'patients' ,       
              ]
    def get_patients(self, obj):
        patient_donations = obj.patient_donation.all()
        patients = [pd.patient_id for pd in patient_donations]
        return varifySelectedPatientSerializeer(patients, many=True).data

class varifySelectedPatientSerializeer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user_id.first_name', read_only=True)
    last_name = serializers.CharField(source='user_id.last_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'father_name',
            'mother_name'
        ]


class PatientDonationSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    donation_id = serializers.PrimaryKeyRelatedField(queryset=Donation.objects.all())
    
    class Meta:
        model = PatientDonation
        fields = [
            'patient_id', 
            'donation_id',
            'amount'
            
        ]
        read_only_fields = ['id']



# class PatientDonationDetailSerializer(serializers.ModelSerializer):
#     patient_id = PatientSerializer()

#     class Meta:
#         model = PatientDonation
#         fields = ['id', 'patient_id', 'amount']


# class DonationDetailSerializer(serializers.ModelSerializer):
#     patient_donations = serializers.SerializerMethodField()

#     class Meta:
#         model = Donation
#         fields = [
#             'id',
#             'donation_type',
#             'donation_status',
#             'amount',
#             'creation_date',
#             'patient_donations'
#         ]

#     def get_patient_donations(self, obj):
#         patient_donations = PatientDonation.objects.filter(donation_id=obj)
#         return PatientDonationDetailSerializer(patient_donations, many=True).data
