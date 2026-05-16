from django.urls import path
from . import views

urlpatterns = [
    path('', views.referral_view, name='referrals'),
]
