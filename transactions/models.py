from django.db import models
from django.conf import settings
import uuid


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
        ('profit', 'Profit'),
        ('referral', 'Referral Bonus'),
        ('bonus', 'Bonus'),
        ('adjustment', 'Admin Adjustment'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('TON', 'TON'),
        ('SOL', 'Solana'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    crypto_currency = models.CharField(max_length=10, choices=CRYPTO_CHOICES, blank=True)
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    wallet_address = models.CharField(max_length=200, blank=True)
    txn_hash = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    proof_image = models.ImageField(upload_to='proofs/', null=True, blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - ${self.amount} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class WalletAddress(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether (TRC20)'),
        ('TON', 'TON'),
        ('SOL', 'Solana'),
    ]
    crypto = models.CharField(max_length=10, choices=CRYPTO_CHOICES, unique=True)
    address = models.CharField(max_length=200)
    network = models.CharField(max_length=50, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.crypto} - {self.address[:20]}..."
