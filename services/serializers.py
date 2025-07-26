from rest_framework import serializers
from .models import Patient , PatientStatus , PendingPatientStatus , Doctor , Appointment




class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user_id.email', read_only=True)
    first_name = serializers.CharField(source='user_id.first_name', read_only=True)
    last_name = serializers.CharField(source='user_id.last_name', read_only=True)
    phone = serializers.CharField(source='user_id.phone', read_only=True)  # If 'phone' is a field on your User model

    class Meta:
        model = Patient
        fields = [
            'id',
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'father_name',
            'mother_name',
            'date_of_birth',
            'place_of_birth',
            'nationality',
            'nationality_ID',
            'family_book_number',
            'disability_card_number',
            'certificate',
            'other_disability',
            'cause',
            'chronic_illness',
            'requirement_of_ongoing_medication',
            'requirement_of_special_care',
            'date_of_blindness',
        
        ]


class UpdatePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'father_name',
            'mother_name',
            'date_of_birth',
            'place_of_birth',
            'nationality',
            'nationality_ID',
            'family_book_number',
            'disability_card_number',
            'certificate',
            'other_disability',
            'cause',
            'chronic_illness',
            'requirement_of_ongoing_medication',
            'requirement_of_special_care',
            'date_of_blindness',
        
        ]



class PatientStatusSerializers(serializers.ModelSerializer):
    class Meta:
        model= PatientStatus
        fields =[
            'patient_id',
        ]


class PendingPatientStatusSerializers(serializers.ModelSerializer):
    class Meta:
      model= PendingPatientStatus
      fields =[
           'patientStatus_id',
           'date',
        ]
      

class DoctorSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(source='user_id.email', read_only=True)
    first_name = serializers.CharField(source='user_id.first_name', read_only=True)
    last_name = serializers.CharField(source='user_id.last_name', read_only=True)
    phone = serializers.CharField(source='user_id.phone', read_only=True)  # If 'phone' is a field on your User model

    class Meta:
        model= Doctor
        fields = [
            'id',
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'speciality',
        ]

     


class AppointmentSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'patient_id',
            'doctor_id',
            'request_date',
            'appointment_date',
            'medical_report',
            'is_completed',
        ]
        read_only_fields = ['id', 'request_date', 'approved_date', 'appointment_status']

    def get_is_completed(self, obj):
        return bool(obj.medical_report is not None and obj.medical_report.strip() != '')