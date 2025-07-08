from django.contrib import admin
from .models import Patient , PatientStatus , PendingPatientStatus , RegistrationPatientStatus , DeathPatientStatus, TransitionPatientStatus, Doctor , Appointment

#admin.site.register(Patient)
admin.site.register(PatientStatus)
admin.site.register(PendingPatientStatus)
admin.site.register(RegistrationPatientStatus)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(DeathPatientStatus)
admin.site.register(TransitionPatientStatus)



@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name')
    search_fields = ('first_name', 'last_name')