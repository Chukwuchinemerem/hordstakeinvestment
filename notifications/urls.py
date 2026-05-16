from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('mark-read/<int:pk>/', views.mark_read, name='mark_notification_read'),
    path('mark-popup/<int:pk>/', views.mark_popup_shown, name='mark_popup_shown'),
    path('get-popup/', views.get_popup_notification, name='get_popup_notification'),
]
