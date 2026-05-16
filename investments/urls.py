from django.urls import path
from . import views
from accounts.views import profile_view, change_password_view

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('invest/<int:plan_id>/', views.invest_view, name='invest'),
    path('my-investments/', views.my_investments, name='my_investments'),
    path('plans/', views.plans_view, name='plans'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
]
