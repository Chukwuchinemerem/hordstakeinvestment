from django.db import models
from django.conf import settings


class KYCSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kyc'
    )

    # Personal Info
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=30)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
    ], blank=True)

    # Address
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    # US-specific
    ssn = models.CharField(max_length=20, blank=True, verbose_name='SSN (US only)')
    occupation = models.CharField(max_length=150, blank=True)
    employer_name = models.CharField(max_length=200, blank=True)
    annual_income = models.CharField(max_length=50, blank=True)
    source_of_funds = models.CharField(max_length=200, blank=True)

    # Documents
    id_type = models.CharField(max_length=50, choices=[
        ('passport', 'Passport'),
        ('drivers_license', "Driver's License"),
        ('national_id', 'National ID'),
        ('residence_permit', 'Residence Permit'),
    ])
    id_number = models.CharField(max_length=100)
    id_expiry = models.DateField(null=True, blank=True)
    id_front = models.ImageField(upload_to='kyc/ids/', verbose_name='ID Front')
    id_back = models.ImageField(upload_to='kyc/ids/', blank=True, null=True, verbose_name='ID Back (if applicable)')
    selfie = models.ImageField(upload_to='kyc/selfies/', verbose_name='Selfie with ID')

    # Review
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='kyc_reviews'
    )

    def __str__(self):
        return f"{self.user.email} — KYC ({self.status})"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'KYC Submission'
        verbose_name_plural = 'KYC Submissions'
