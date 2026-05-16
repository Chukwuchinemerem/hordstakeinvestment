from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.kyc_submit, name='kyc_submit'),
    path('status/', views.kyc_status, name='kyc_status'),
]
