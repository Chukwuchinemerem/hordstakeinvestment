from django.contrib import admin
from .models import InvestmentPlan, Investment

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'roi_percentage', 'duration', 'duration_unit', 'min_deposit', 'max_deposit', 'is_active']

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'started_at']
    list_filter = ['status']
