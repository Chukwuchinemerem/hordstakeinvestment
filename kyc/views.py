from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import KYCSubmission
from notifications.models import Notification


@login_required
def kyc_submit(request):
    try:
        kyc = request.user.kyc
        # Already submitted
        return render(request, 'dashboard/kyc_status.html', {'kyc': kyc})
    except KYCSubmission.DoesNotExist:
        pass

    if request.method == 'POST':
        try:
            kyc = KYCSubmission(
                user=request.user,
                full_name=request.POST.get('full_name', ''),
                date_of_birth=request.POST.get('date_of_birth'),
                nationality=request.POST.get('nationality', ''),
                phone_number=request.POST.get('phone_number', ''),
                gender=request.POST.get('gender', ''),
                address_line1=request.POST.get('address_line1', ''),
                address_line2=request.POST.get('address_line2', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                zip_code=request.POST.get('zip_code', ''),
                country=request.POST.get('country', ''),
                ssn=request.POST.get('ssn', ''),
                occupation=request.POST.get('occupation', ''),
                employer_name=request.POST.get('employer_name', ''),
                annual_income=request.POST.get('annual_income', ''),
                source_of_funds=request.POST.get('source_of_funds', ''),
                id_type=request.POST.get('id_type', 'passport'),
                id_number=request.POST.get('id_number', ''),
                id_expiry=request.POST.get('id_expiry') or None,
                id_front=request.FILES.get('id_front'),
                id_back=request.FILES.get('id_back') or None,
                selfie=request.FILES.get('selfie'),
            )
            kyc.save()

            Notification.objects.create(
                user=request.user,
                title='KYC Submitted',
                message='Your KYC documents have been submitted and are under review. You will be notified once reviewed.',
                notification_type='info'
            )

            messages.success(request, 'KYC submitted successfully! Under review.')
            return redirect('kyc_status')
        except Exception as e:
            messages.error(request, f'Error submitting KYC: {str(e)}')

    return render(request, 'dashboard/kyc_submit.html')


@login_required
def kyc_status(request):
    try:
        kyc = request.user.kyc
    except KYCSubmission.DoesNotExist:
        kyc = None
    return render(request, 'dashboard/kyc_status.html', {'kyc': kyc})
