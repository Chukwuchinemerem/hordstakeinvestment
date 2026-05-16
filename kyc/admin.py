from django.contrib import admin
from .models import KYCSubmission

@admin.register(KYCSubmission)
class KYCAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'status', 'submitted_at']
    list_filter = ['status']
    search_fields = ['user__email', 'full_name', 'id_number']
