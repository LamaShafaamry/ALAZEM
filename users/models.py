from django.db import models
from django.contrib.auth.models import User ,AbstractUser
from django.db import models
from django.utils import timezone



class Role(models.TextChoices):
       ADMIN =  'ADM', 'Admin'
       MANAGER = 'MAN' , ' Manager'      
       DOCTOR  = 'DOC' , 'Doctor'    
       PATIENT = 'PAT' , 'Patient'
       VOLUNTEE = 'VOL', 'Volunteer'
       USER = 'USE' , 'USER'


   
class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    email= models.EmailField(
        max_length=150,
        unique=True,
        help_text=(
            "Required. 150 characters or fewer."
        ),
        error_messages={
            "unique": ("A user with that emaiL already exists."),
        },
    )
    profile_image = models.ImageField(
        null=True, blank=True, upload_to='profiles/', default='profiles/user-default.png')
    role = models.CharField(
            max_length=3,
            choices=Role.choices,
            default=Role.USER,

    )
    varification_code = models.CharField(max_length=10 , blank=True , null= True)
    is_email_varification = models.BooleanField(default= True)

    def __str__(self):
            return f"{self.pk}- {self.first_name} {self.last_name}  ({self.role})"




class VolunteerStatus(models.TextChoices):
    REGISTERED = 'REG', 'Registered'
    PENDING = 'PEN', 'Pending'
    REJECTED = 'REJ', 'Rejected'
    WITHDRAWN = 'WIT', 'Withdrawn'



class Volunteer(models.Model):
    user_id= models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False , related_name='volunteer_user')
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    nationality_ID = models.CharField(max_length=100, blank=True, null=True)
    grand_history = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    certificate = models.TextField(blank=True, null=True)
    job = models.CharField(max_length=255, blank=True, null=True)
    previously_affiliated_associations = models.TextField(blank=True, null=True)
    status = models.CharField(
            max_length=3,
            choices=VolunteerStatus.choices,
            default=VolunteerStatus.PENDING,
    )
    patient_id = models.OneToOneField('services.Patient', on_delete=models.SET_NULL, null=True, blank=True , related_name= 'assigned_volunteer')


    def __str__(self):
        return f"{self.id} - {self.user_id.first_name} {self.user_id.last_name}"


class Note(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    patient_id = models.ForeignKey('services.Patient', on_delete=models.SET_NULL, null=True, blank=True )
    volunteer_id = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.CharField(max_length = 50000, blank=True , null = True)
    creation_date= models.DateTimeField(default=timezone.now())

    def __str__(self):
         return f"{self.id} - {self.patient_id} : {self.volunteer_id}"

class WithdrawalrStatus(models.TextChoices):
    APPROVED = 'APP', 'Approved'
    PENDING = 'PEN', 'Pending'
    REJECTED = 'REJ', 'Rejected'


class WithdrawalRequest(models.Model):
    id = models.AutoField(primary_key=True,unique=True,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')  # Allow multiple
    cause = models.TextField()
    status = models.CharField(
            max_length=3,
            choices=WithdrawalrStatus.choices,
            default=WithdrawalrStatus.PENDING,
    )  # None = pending, True = approved, False = rejected
    creation_date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.id} -Withdrawal Request from {self.user.first_name} {self.user.last_name} - {self.creation_date}"


