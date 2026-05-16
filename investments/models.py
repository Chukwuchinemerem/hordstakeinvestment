from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
from django.utils import timezone


class InvestmentPlan(models.Model):
    DURATION_CHOICES = [
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    roi_percentage = models.DecimalField(max_digits=8, decimal_places=2, help_text='ROI % per cycle')
    duration = models.PositiveIntegerField(help_text='Duration value')
    duration_unit = models.CharField(max_length=10, choices=DURATION_CHOICES, default='days')
    min_deposit = models.DecimalField(max_digits=20, decimal_places=2)
    max_deposit = models.DecimalField(max_digits=20, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    color = models.CharField(max_length=20, default='#F59E0B')
    icon = models.CharField(max_length=50, default='chart-line')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.roi_percentage}% ROI"

    def get_duration_display_full(self):
        return f"{self.duration} {self.duration_unit}"

    class Meta:
        ordering = ['min_deposit']


class Investment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investments')
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    profit_earned = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    expected_end = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_profit_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - ${self.amount} ({self.status})"

    def get_expected_profit(self):
        if self.plan:
            return self.amount * (self.plan.roi_percentage / Decimal('100'))
        return Decimal('0')

    def get_progress_percent(self):
        if self.status == 'completed':
            return 100
        if self.expected_end and self.started_at:
            total = (self.expected_end - self.started_at).total_seconds()
            elapsed = (timezone.now() - self.started_at).total_seconds()
            if total > 0:
                return min(int((elapsed / total) * 100), 99)
        return 0

    class Meta:
        ordering = ['-started_at']
