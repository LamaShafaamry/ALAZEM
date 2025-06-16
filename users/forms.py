# from django import forms
# from django.contrib.auth.models import User as AuthUser
# from django.contrib.auth.forms import UserCreationForm
# from .models import User, Role

# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     phone = forms.CharField(required=False, max_length=20)
#     role_name = forms.ChoiceField(choices=Role.USER_ROLES, required=True)

#     class Meta:
#         model = AuthUser
#         fields = ('username', 'email', 'phone', 'role_name', 'password1', 'password2')

#     def save(self, commit=True):
#         auth_user = super().save(commit=False)
#         auth_user.email = self.cleaned_data['email']
#         if commit:
#             auth_user.save()
#             # Create the extended User model instance
#             role = Role.objects.filter(role_name=self.cleaned_data['role_name']).first()
#             custom_user = User(
#                 user=auth_user,
#                 username=auth_user.username,
#                 email=auth_user.email,
#                 phone=self.cleaned_data.get('phone'),
#                 role_id=role,
#             )
#             custom_user.set_password(self.cleaned_data["password1"])
#             custom_user.save()
#         return auth_user

