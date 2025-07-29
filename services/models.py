from django.db import models
from users.models import User
from django.utils import timezone




class Patient(models.Model):
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False , related_name='patient_user')
    id =models.AutoField(primary_key=True,unique=True,editable=False)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    nationality_ID = models.CharField(max_length=100, blank=True, null=True)
    family_book_number = models.CharField(max_length=100, blank=True, null=True)
    disability_card_number = models.CharField(max_length=100, blank=True, null=True)
    certificate = models.TextField(blank=True, null=True)
    date_of_blindness = models.DateField(blank=True, null=True)
    cause = models.TextField(blank=True, null=True)
    other_disability = models.TextField(blank=True, null=True)
    chronic_illness = models.TextField(blank=True, null=True)
    requirement_of_ongoing_medication = models.TextField(blank=True, null=True)
    requirement_of_special_care = models.TextField(blank=True, null=True)
    residence_in_the_institution = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.id} - {self.user_id.first_name} {self.user_id.last_name}"


class PatientStatus(models.Model):
    id = models.AutoField(unique=True,primary_key=True , editable=False)
    patient_id =  models.ForeignKey(Patient, on_delete=models.CASCADE, null=False, blank=False , related_name='patient_status')

    def __str__(self):
        return f"{self.patient_id.user_id.first_name} {self.patient_id.user_id.last_name}"

class PendingPatientStatus(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    patientStatus = models.ForeignKey(PatientStatus, on_delete=models.CASCADE, related_name='pending_statuses')
    date = models.DateTimeField(default=timezone.now())
  
    def __str__(self):
        return f"{self.patientStatus.id} - {self.patientStatus.patient_id.user_id.first_name} {self.patientStatus.patient_id.user_id.last_name}"

class RegistrationPatientStatus(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    patientStatus = models.ForeignKey(PatientStatus, on_delete=models.CASCADE, related_name='registration_statuses')
    date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.id} - {self.patientStatus.patient_id.user_id.first_name} {self.patientStatus.patient_id.user_id.last_name}"

class DeathPatientStatus(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    patientStatus = models.ForeignKey(PatientStatus, on_delete=models.CASCADE, related_name='death_statuses')
    date = models.DateTimeField(default=timezone.now())
    cause_of_death = models.TextField(max_length=200, null=True , blank=True)

    def __str__(self):
        return f"{self.patientStatus.patient_id.user_id.first_name} {self.patientStatus.patient_id.user_id.last_name}"

class WithdrawalPatientStatus(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    patientStatus = models.ForeignKey(PatientStatus, on_delete=models.CASCADE, related_name='withdrawal_statuses')
    date = models.DateTimeField(default=timezone.now())
    new_association = models.TextField(max_length=200 , null=True , blank= True)

    def __str__(self):
        return f"{self.patientStatus.patient_id.user_id.first_name} {self.patientStatus.patient_id.user_id.last_name}"

class RejectedPatientStatus(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    patientStatus = models.ForeignKey(PatientStatus, on_delete=models.CASCADE, related_name='rejection_statuses')
    date = models.DateTimeField(default=timezone.now())
    case_of_rejection = models.TextField(max_length=500 , null=True , blank= True)

    def __str__(self):
        return f"{self.patientStatus.id}- {self.patientStatus.patient_id.user_id.first_name} {self.patientStatus.patient_id.user_id.last_name}"

       
  
class DoctorStatus(models.TextChoices):
    APPROVAL = 'APP', 'Approval'
    PENDING = 'PEN', 'Pending'
    REJECTED = 'REJ', 'Rejected'


class Doctor(models.Model):
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    id =models.AutoField(primary_key=True,unique=True,editable=False)
    speciality =models.CharField(max_length=100)
    doctor_status = models.CharField(
            max_length=3,
            choices=DoctorStatus.choices,
            default=DoctorStatus.PENDING,
    )

    def __str__(self):
        return f"{self.id} - {self.user_id.first_name} {self.user_id.last_name}"
    

class AppointmentStatus(models.TextChoices):
    APPROVAL = 'APP', 'Approval'
    PENDING = 'PEN', 'Pending'
    REJECTED = 'REJ', 'Rejected'
    CANCELED = 'CAN', 'Canceled'


class Appointment(models.Model):
    id =models.AutoField(primary_key=True,unique=True,editable=False)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, null=False, blank=False)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=False, blank=False)
    appointment_status = models.CharField(
            max_length=3,
            choices=AppointmentStatus.choices,
            default=AppointmentStatus.PENDING,
    )
    request_date = models.DateTimeField(default=timezone.now())  # Automatically set the date when the appointment is requested
    approved_date = models.DateTimeField(null=True, blank=True)  # Date when the appointment is approved
    appointment_date = models.DateTimeField(null=False , blank= False)
    medical_report = models.CharField(max_length=500 , null= True , blank= True)

    def __str__(self):
        return f"Appointment with {self.patient_id.user_id.first_name} {self.patient_id.user_id.last_name} for {self.doctor_id.user_id.first_name} {self.doctor_id.user_id.last_name} "