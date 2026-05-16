from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Referral


@login_required
def referral_view(request):
    referrals = Referral.objects.filter(referrer=request.user).select_related('referred')
    return render(request, 'dashboard/referrals.html', {
        'referrals': referrals,
        'referral_link': request.build_absolute_uri(request.user.get_referral_link()),
    })
