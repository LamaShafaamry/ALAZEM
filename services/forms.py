from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'father_name',
            'mother_name',
            'date_of_birth',
            'place_of_birth',
            'nationality',
            'national_ID',
            'family_book_number',
            'disability_card_number',
            'certificate',
            'other_disability',
            'cause',
            'chronic_illness',
            'requirement_of_ongoing_medication',
            'requirement_of_special_care',
            'history_of_blindness',
        ]