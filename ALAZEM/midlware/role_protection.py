# permissions.py
from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'ADM'

class IsManagerRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'MAN' 


class IsDoctorRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'DOC'


class IsPatientRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'PAT'


class IsVolunteerRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'VOL'


class IsDonationManagerRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'DONATIONMANAGER'


class IsAdminManagerRole(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and (request.user.role == 'ADM' or request.user.role == 'MAN')