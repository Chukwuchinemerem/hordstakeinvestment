def site_settings(request):
    try:
        from .models import SiteSettings
        settings_obj = SiteSettings.get_settings()
    except Exception:
        settings_obj = None

    unread_count = 0
    kyc_status = None

    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            pass
        try:
            kyc_status = request.user.kyc.status
        except Exception:
            kyc_status = None

    return {
        'site_settings': settings_obj,
        'unread_notifications': unread_count,
        'kyc_status': kyc_status,
    }
