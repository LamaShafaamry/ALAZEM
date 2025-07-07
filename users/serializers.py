from rest_framework import serializers
from .models import Volunteer , User , Note
from services.models import Patient


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
           'first_name',
           'last_name',
           'email',
           'phone',
           'role',
        ]
    

class Volunteerserializers(serializers.ModelSerializer):
    class Meta:
        model = Volunteer
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'father_name',
            'mother_name',
            'date_of_birth',
            'place_of_birth',
            'nationality',
            'nationality_ID',
            'grand_history',
            'address',
            'certificate',
            'job',
            'previously_affiliated_associations',
            'status',
        ]



class VolunteerAssignmentSerializer(serializers.Serializer):
    volunteer_id = serializers.IntegerField()
    patient_id = serializers.CharField()

    def validate(self, data):
        try:
            volunteer = Volunteer.objects.get(id=data['volunteer_id'])
        except Volunteer.DoesNotExist:
            raise serializers.ValidationError("Volunteer not found.")

        try:
            patient = Patient.objects.get(id=data['patient_id'])
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient not found.")

        if volunteer.patient_id is not None:
            raise serializers.ValidationError("Volunteer is already assigned to a patient.")

        if hasattr(patient, 'assigned_volunteer'):
            raise serializers.ValidationError("Patient already has a volunteer.")

        return data

    def create(self, validated_data):
        volunteer = Volunteer.objects.get(id=validated_data['volunteer_id'])
        patient = Patient.objects.get(id=validated_data['patient_id'])
        volunteer.patient_id = patient
        volunteer.save()
        return volunteer


       

class NoteSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id', 
            'volunteer_name', 
            'patient_name', 
            'content'
        ]

    def get_volunteer_name(self, obj):
        return f"{obj.volunteer_id.first_name} {obj.volunteer_id.last_name}" if obj.volunteer_id else None

    def get_patient_name(self, obj):
        return f"{obj.patient_id.first_name} {obj.patient_id.last_name}" if obj.patient_id else None
    



class WithdrawalRequestSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if value is not True:
            raise serializers.ValidationError("You must confirm the withdrawal request.")
        return value


class WithdrawalRequestSerializerForManager(serializers.ModelSerializer):
    volunteer_name = serializers.SerializerMethodField()

    class Meta:
        model = Volunteer
        fields = ['id', 'volunteer_name', 'status']

    def get_volunteer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
