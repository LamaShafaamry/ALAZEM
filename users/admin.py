from django.contrib import admin
from .models import User , Role , Volunteer
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Fields', {
            'fields': ('phone', 'profile_image', 'role'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Extra Fields', {
            'fields': ('phone', 'profile_image', 'role'),
        }),
    )

admin.site.register(Volunteer)