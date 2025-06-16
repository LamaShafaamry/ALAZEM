from django.db.models.signals import post_save, post_delete
from .models import User , Volunteer
from services.models import Patient

# def createProfile(sender , instance, created, **kwargs):
#     if created:
#          user= instance
#          profile = User.objects.create(
#               username=user.username, 
#               email = user.email,
#          )


def deleteUser(sender, instance, **kwagrs):
     user= instance.user_id
     user.delete()

# post_save.connect(createProfile , sender=User)
post_delete.connect(deleteUser, sender=Patient)


def deleteVolunteer(sender, instance, **kwagrs):
     user= instance.user_id
     user.delete()

post_delete.connect(deleteUser, sender=Volunteer)
