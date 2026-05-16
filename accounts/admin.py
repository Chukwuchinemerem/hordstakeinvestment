from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'wallet_balance', 'is_verified', 'is_banned', 'date_joined']
    list_filter = ['is_verified', 'is_banned', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Platform Info', {'fields': ('phone', 'country', 'wallet_balance', 'total_deposited', 'total_withdrawn', 'total_profit', 'referral_code', 'referred_by', 'referral_earnings', 'is_verified', 'is_banned', 'kyc_verified')}),
        ('Wallets', {'fields': ('btc_wallet', 'eth_wallet', 'usdt_wallet', 'ton_wallet', 'sol_wallet')}),
    )
