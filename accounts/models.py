from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_deposited = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_withdrawn = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_profit = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')
    referral_earnings = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    kyc_verified = models.BooleanField(default=False)
    btc_wallet = models.CharField(max_length=200, blank=True)
    eth_wallet = models.CharField(max_length=200, blank=True)
    usdt_wallet = models.CharField(max_length=200, blank=True)
    ton_wallet = models.CharField(max_length=200, blank=True)
    sol_wallet = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def get_referral_link(self):
        from django.conf import settings
        return f"/auth/register/?ref={self.referral_code}"

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
