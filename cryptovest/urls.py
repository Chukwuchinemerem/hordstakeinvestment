from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('auth/', include('accounts.urls')),
    path('dashboard/', include('investments.urls')),
    path('transactions/', include('transactions.urls')),
    path('referrals/', include('referrals.urls')),
    path('notifications/', include('notifications.urls')),
    path('kyc/', include('kyc.urls')),
    path('admin_dashboard/', include('core.admin_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
