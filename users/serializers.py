from rest_framework import serializers
from .models import Volunteer , User


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



       
      