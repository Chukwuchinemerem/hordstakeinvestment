from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def mark_popup_shown(request, pk):
    """Called via AJAX once popup is dismissed — never shows again"""
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.popup_shown = True
    n.is_read = True
    n.save()
    return JsonResponse({'status': 'ok'})


@login_required
def get_popup_notification(request):
    """Returns the first un-shown popup notification as JSON"""
    notif = Notification.objects.filter(
        user=request.user,
        popup_shown=False,
        notification_type__in=['deposit', 'success', 'profit', 'kyc', 'broadcast']
    ).first()
    if notif:
        return JsonResponse({
            'id': notif.pk,
            'title': notif.title,
            'message': notif.message,
            'type': notif.notification_type,
        })
    return JsonResponse({'id': None})
