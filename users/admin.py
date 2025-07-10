from django.contrib import admin
from .models import User , Role , Volunteer , Note , WithdrawalRequest
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


admin.site.register(User)
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('Extra Fields', {
#             'fields': ('phone', 'profile_image', 'role'),
#         }),
#     )

#     add_fieldsets = BaseUserAdmin.add_fieldsets + (
#         ('Extra Fields', {
#             'fields': ('phone', 'profile_image', 'role'),
#         }),
#     )

admin.site.register(Volunteer)


# @admin.register(Volunteer)
# class VolunteerAdmin(admin.ModelAdmin):
#     list_display = ('id', 'first_name', 'last_name', 'patient_id')
#     search_fields = ('first_name', 'last_name')
#     autocomplete_fields = ['patient_id']


admin.site.register(Note)
admin.site.register(WithdrawalRequest)
