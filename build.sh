#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py makemigrations accounts core investments transactions referrals notifications kyc
python manage.py migrate
python create_superuser.py
python manage.py shell -c "
from core.models import SiteSettings, Testimonial, FAQ
from investments.models import InvestmentPlan
from transactions.models import WalletAddress

SiteSettings.objects.get_or_create(pk=1, defaults={
    'site_name': 'Hordstake',
    'whatsapp_number': '+12345678900',
    'support_email': 'support@hordstake.com',
    'referral_bonus_percent': 5.00,
    'min_withdrawal': 10.00,
    'hero_title': 'Grow Your Wealth With Crypto',
})

plans = [
    {'name':'Starter','roi_percentage':8,'duration':7,'duration_unit':'days','min_deposit':100,'max_deposit':999,'color':'#3b82f6','icon':'seedling','is_featured':False},
    {'name':'Silver','roi_percentage':12,'duration':14,'duration_unit':'days','min_deposit':1000,'max_deposit':4999,'color':'#6366f1','icon':'chart-line','is_featured':False},
    {'name':'Gold','roi_percentage':18,'duration':30,'duration_unit':'days','min_deposit':5000,'max_deposit':19999,'color':'#f59e0b','icon':'coins','is_featured':True},
    {'name':'Platinum','roi_percentage':25,'duration':60,'duration_unit':'days','min_deposit':20000,'max_deposit':999999,'color':'#10b981','icon':'gem','is_featured':False},
]
for p in plans:
    InvestmentPlan.objects.get_or_create(name=p['name'], defaults=p)

wallets = [
    {'crypto':'BTC','address':'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh','network':'Bitcoin'},
    {'crypto':'ETH','address':'0x71C7656EC7ab88b098defB751B7401B5f6d8976F','network':'ERC20'},
    {'crypto':'USDT','address':'TN1LukbrBnRkf1VRaHDxXBUKN5dYGDNVJi','network':'TRC20'},
    {'crypto':'TON','address':'EQD4FPq-PRDieyQKkizfu7KBjgYpL9N2T4HN3cHQmOcdCB0z','network':'TON'},
    {'crypto':'SOL','address':'9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM','network':'Solana'},
]
for w in wallets:
    WalletAddress.objects.get_or_create(crypto=w['crypto'], defaults=w)

print('Seed data ready.')
"
