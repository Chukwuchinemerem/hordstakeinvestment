from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import SiteSettings, Testimonial, FAQ, Partner, NewsletterSubscriber, CarouselSlide
from investments.models import InvestmentPlan, Investment
from transactions.models import Transaction, WalletAddress
from accounts.models import User
from notifications.models import Notification


def home(request):
    try:
        settings_obj = SiteSettings.get_settings()
    except Exception:
        settings_obj = None
    try:
        plans = list(InvestmentPlan.objects.filter(is_active=True))
    except Exception:
        plans = []
    try:
        testimonials = list(Testimonial.objects.filter(is_active=True))
    except Exception:
        testimonials = []
    try:
        faqs = list(FAQ.objects.filter(is_active=True))
    except Exception:
        faqs = []
    try:
        partners = list(Partner.objects.filter(is_active=True))
    except Exception:
        partners = []
    try:
        slides = list(CarouselSlide.objects.filter(is_active=True))
    except Exception:
        slides = []
    try:
        stats = {
            'total_users': User.objects.count(),
            'total_paid': Transaction.objects.filter(status='completed', transaction_type='withdrawal').aggregate(s=Sum('amount'))['s'] or 0,
            'total_deposits': Transaction.objects.filter(status='completed', transaction_type='deposit').aggregate(s=Sum('amount'))['s'] or 0,
            'active_investors': Investment.objects.filter(status='active').values('user').distinct().count(),
        }
    except Exception:
        stats = {'total_users': 0, 'total_paid': 0, 'total_deposits': 0, 'active_investors': 0}

    return render(request, 'landing/index.html', {
        'plans': plans,
        'testimonials': testimonials,
        'faqs': faqs,
        'partners': partners,
        'slides': slides,
        'stats': stats,
    })


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                NewsletterSubscriber.objects.get_or_create(email=email)
                messages.success(request, 'Successfully subscribed to our newsletter!')
            except Exception:
                pass
    return redirect('home')


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    stats = {
        'total_users': User.objects.count(),
        'new_users_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
        'total_deposits': Transaction.objects.filter(transaction_type='deposit', status='completed').aggregate(s=Sum('amount'))['s'] or 0,
        'pending_deposits': Transaction.objects.filter(transaction_type='deposit', status='pending').count(),
        'total_withdrawals': Transaction.objects.filter(transaction_type='withdrawal', status='completed').aggregate(s=Sum('amount'))['s'] or 0,
        'pending_withdrawals': Transaction.objects.filter(transaction_type='withdrawal', status='pending').count(),
        'active_investments': Investment.objects.filter(status='active').count(),
        'total_profit_paid': Transaction.objects.filter(transaction_type='profit', status='completed').aggregate(s=Sum('amount'))['s'] or 0,
        'pending_kyc': 0,
    }
    try:
        from kyc.models import KYCSubmission
        stats['pending_kyc'] = KYCSubmission.objects.filter(status='pending').count()
    except Exception:
        pass

    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_transactions = Transaction.objects.order_by('-created_at')[:10]
    chart_labels, chart_deposits = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%b %d'))
        day_dep = Transaction.objects.filter(
            transaction_type='deposit', status='completed', created_at__date=d
        ).aggregate(s=Sum('amount'))['s'] or 0
        chart_deposits.append(float(day_dep))

    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_transactions': recent_transactions,
        'chart_labels': chart_labels,
        'chart_deposits': chart_deposits,
    })


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_users(request):
    users = User.objects.order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'adjust_balance':
            amount = Decimal(request.POST.get('amount', 0))
            note = request.POST.get('note', '')
            user.wallet_balance += amount
            user.save()
            Transaction.objects.create(
                user=user, transaction_type='adjustment',
                amount=abs(amount), status='completed',
                description=f'Admin adjustment: {note}'
            )
            Notification.objects.create(
                user=user, title='Balance Adjusted',
                message=f'Your wallet has been updated. Amount: ${amount}',
                notification_type='success'
            )
            messages.success(request, f'Balance adjusted by ${amount}')
        elif action == 'ban':
            user.is_banned = not user.is_banned
            user.save()
            messages.success(request, f'User {"banned" if user.is_banned else "unbanned"}.')
        elif action == 'verify':
            user.is_verified = True
            user.save()
            messages.success(request, 'User verified.')
        return redirect('admin_user_detail', pk=pk)

    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:20]
    investments = Investment.objects.filter(user=user)
    kyc_obj = None
    try:
        from kyc.models import KYCSubmission
        try:
            kyc_obj = user.kyc
        except Exception:
            kyc_obj = None
    except Exception:
        pass
    return render(request, 'admin_panel/user_detail.html', {
        'profile_user': user,
        'transactions': transactions,
        'investments': investments,
        'kyc_obj': kyc_obj,
    })


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_deposits(request):
    deposits = Transaction.objects.filter(transaction_type='deposit').order_by('-created_at')
    if request.method == 'POST':
        txn_id = request.POST.get('txn_id')
        action = request.POST.get('action')
        try:
            txn = Transaction.objects.get(id=txn_id, transaction_type='deposit')
            if action == 'approve' and txn.status == 'pending':
                txn.status = 'completed'
                txn.save()
                txn.user.wallet_balance += txn.amount
                txn.user.total_deposited += txn.amount
                txn.user.save()
                settings_obj = SiteSettings.get_settings()
                if txn.user.referred_by and settings_obj.referral_bonus_percent > 0:
                    bonus = txn.amount * (settings_obj.referral_bonus_percent / 100)
                    txn.user.referred_by.referral_earnings += bonus
                    txn.user.referred_by.wallet_balance += bonus
                    txn.user.referred_by.save()
                    Transaction.objects.create(
                        user=txn.user.referred_by, transaction_type='referral',
                        amount=bonus, status='completed',
                        description=f'Referral bonus from {txn.user.email}'
                    )
                    Notification.objects.create(
                        user=txn.user.referred_by,
                        title='Referral Bonus Received',
                        message=f'You earned ${bonus} referral bonus!',
                        notification_type='success'
                    )
                Notification.objects.create(
                    user=txn.user,
                    title='Deposit Confirmed ✓',
                    message=f'Your deposit of ${txn.amount} has been confirmed and credited to your wallet.',
                    notification_type='deposit',
                    popup_shown=False
                )
                messages.success(request, 'Deposit approved.')
            elif action == 'reject' and txn.status == 'pending':
                txn.status = 'rejected'
                txn.admin_note = request.POST.get('note', '')
                txn.save()
                Notification.objects.create(
                    user=txn.user,
                    title='Deposit Rejected',
                    message=f'Your deposit of ${txn.amount} was rejected. Reason: {txn.admin_note}',
                    notification_type='warning'
                )
                messages.warning(request, 'Deposit rejected.')
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaction not found.')
        return redirect('admin_deposits')
    return render(request, 'admin_panel/deposits.html', {'deposits': deposits})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_withdrawals(request):
    withdrawals = Transaction.objects.filter(transaction_type='withdrawal').order_by('-created_at')
    if request.method == 'POST':
        txn_id = request.POST.get('txn_id')
        action = request.POST.get('action')
        try:
            txn = Transaction.objects.get(id=txn_id, transaction_type='withdrawal')
            if action == 'approve' and txn.status == 'pending':
                txn.status = 'completed'
                txn.save()
                txn.user.total_withdrawn += txn.amount
                txn.user.save()
                Notification.objects.create(
                    user=txn.user,
                    title='Withdrawal Approved ✓',
                    message=f'Your withdrawal of ${txn.amount} has been approved.',
                    notification_type='success'
                )
                messages.success(request, 'Withdrawal approved.')
            elif action == 'reject' and txn.status == 'pending':
                txn.status = 'rejected'
                txn.save()
                txn.user.wallet_balance += txn.amount
                txn.user.save()
                Notification.objects.create(
                    user=txn.user,
                    title='Withdrawal Rejected',
                    message=f'Your withdrawal of ${txn.amount} was rejected and refunded.',
                    notification_type='warning'
                )
                messages.warning(request, 'Withdrawal rejected and refunded.')
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaction not found.')
        return redirect('admin_withdrawals')
    return render(request, 'admin_panel/withdrawals.html', {'withdrawals': withdrawals})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_investments(request):
    investments = Investment.objects.select_related('user', 'plan').order_by('-started_at')
    return render(request, 'admin_panel/investments.html', {'investments': investments})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_plans(request):
    plans = InvestmentPlan.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            InvestmentPlan.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
                roi_percentage=Decimal(request.POST['roi_percentage']),
                duration=int(request.POST['duration']),
                duration_unit=request.POST['duration_unit'],
                min_deposit=Decimal(request.POST['min_deposit']),
                max_deposit=Decimal(request.POST['max_deposit']),
                color=request.POST.get('color', '#2563eb'),
                is_featured=request.POST.get('is_featured') == 'on',
            )
            messages.success(request, 'Investment plan created.')
        elif action == 'delete':
            plan_id = request.POST.get('plan_id')
            InvestmentPlan.objects.filter(id=plan_id).delete()
            messages.success(request, 'Plan deleted.')
        elif action == 'toggle':
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(InvestmentPlan, id=plan_id)
            plan.is_active = not plan.is_active
            plan.save()
            messages.success(request, 'Plan status updated.')
        return redirect('admin_plans')
    return render(request, 'admin_panel/plans.html', {'plans': plans})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_wallets(request):
    wallets = WalletAddress.objects.all()
    crypto_label_pairs = [
        ("BTC", "Bitcoin (BTC)"),
        ("ETH", "Ethereum (ETH)"),
        ("USDT", "Tether USDT (TRC20)"),
        ("TON", "TON Network"),
        ("SOL", "Solana (SOL)")
    ]
    if request.method == 'POST':
        crypto = request.POST.get('crypto')
        address = request.POST.get('address', '').strip()
        network = request.POST.get('network', '')
        if crypto and address:
            WalletAddress.objects.update_or_create(
                crypto=crypto,
                defaults={'address': address, 'network': network, 'is_active': True}
            )
            messages.success(request, f'{crypto} wallet address updated.')
        return redirect('admin_wallets')
    return render(request, 'admin_panel/wallets.html', {'wallets': wallets, 'crypto_label_pairs': crypto_label_pairs})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_content(request):
    settings_obj = SiteSettings.get_settings()
    testimonials = Testimonial.objects.all()
    faqs = FAQ.objects.all()
    partners = Partner.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_settings':
            for field in ['site_name', 'hero_title', 'hero_subtitle', 'whatsapp_number',
                          'support_email', 'referral_bonus_percent', 'min_withdrawal']:
                val = request.POST.get(field)
                if val is not None:
                    setattr(settings_obj, field, val)
            settings_obj.save()
            messages.success(request, 'Settings updated.')
        elif action == 'add_testimonial':
            Testimonial.objects.create(
                name=request.POST['t_name'],
                country=request.POST['t_country'],
                message=request.POST['t_message'],
                rating=int(request.POST.get('t_rating', 5)),
            )
            messages.success(request, 'Testimonial added.')
        elif action == 'delete_testimonial':
            Testimonial.objects.filter(id=request.POST.get('t_id')).delete()
            messages.success(request, 'Testimonial deleted.')
        elif action == 'add_faq':
            FAQ.objects.create(
                question=request.POST['faq_question'],
                answer=request.POST['faq_answer'],
            )
            messages.success(request, 'FAQ added.')
        elif action == 'delete_faq':
            FAQ.objects.filter(id=request.POST.get('faq_id')).delete()
            messages.success(request, 'FAQ deleted.')
        return redirect('admin_content')
    return render(request, 'admin_panel/content.html', {
        'settings_obj': settings_obj,
        'testimonials': testimonials,
        'faqs': faqs,
        'partners': partners,
    })


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_process_profits(request):
    if request.method == 'POST':
        active = Investment.objects.filter(status='active')
        count = 0
        for inv in active:
            if inv.expected_end and timezone.now() >= inv.expected_end:
                profit = inv.get_expected_profit()
                inv.profit_earned = profit
                inv.status = 'completed'
                inv.completed_at = timezone.now()
                inv.save()
                inv.user.wallet_balance += profit
                inv.user.total_profit += profit
                inv.user.save()
                Transaction.objects.create(
                    user=inv.user, transaction_type='profit',
                    amount=profit, status='completed',
                    description=f'Profit from {inv.plan.name if inv.plan else "investment"}'
                )
                Notification.objects.create(
                    user=inv.user,
                    title='Investment Matured 🎉',
                    message=f'Your ${inv.amount} investment has matured! ${profit} profit credited to your wallet.',
                    notification_type='profit',
                    popup_shown=False
                )
                count += 1
        messages.success(request, f'Processed {count} matured investments.')
    return redirect('admin_dashboard')


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_kyc(request):
    from kyc.models import KYCSubmission
    submissions = KYCSubmission.objects.select_related('user').order_by('-submitted_at')
    return render(request, 'admin_panel/kyc.html', {'submissions': submissions})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_kyc_detail(request, pk):
    from kyc.models import KYCSubmission
    submission = get_object_or_404(KYCSubmission, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            submission.status = 'approved'
            submission.admin_note = request.POST.get('note', '')
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.user
            submission.save()
            submission.user.kyc_verified = True
            submission.user.save()
            Notification.objects.create(
                user=submission.user,
                title='KYC Approved ✓',
                message='Your identity has been verified. Your account is now fully verified!',
                notification_type='success',
                popup_shown=False
            )
            messages.success(request, 'KYC approved.')
        elif action == 'reject':
            submission.status = 'rejected'
            submission.admin_note = request.POST.get('note', '')
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.user
            submission.save()
            submission.user.kyc_verified = False
            submission.user.save()
            Notification.objects.create(
                user=submission.user,
                title='KYC Rejected',
                message=f'Your KYC was rejected. Reason: {submission.admin_note}. Please resubmit.',
                notification_type='warning'
            )
            messages.warning(request, 'KYC rejected.')
        return redirect('admin_kyc_detail', pk=pk)
    return render(request, 'admin_panel/kyc_detail.html', {'submission': submission})


@user_passes_test(is_admin, login_url='/auth/login/')
def admin_broadcast(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message_text = request.POST.get('message', '').strip()
        target = request.POST.get('target', 'all')
        if title and message_text:
            if target == 'all':
                users = User.objects.filter(is_active=True)
            elif target == 'verified':
                users = User.objects.filter(is_active=True, is_verified=True)
            else:
                users = User.objects.filter(is_active=True)
            count = 0
            for user in users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message_text,
                    notification_type='broadcast',
                    popup_shown=False
                )
                count += 1
            messages.success(request, f'Broadcast sent to {count} users.')
        else:
            messages.error(request, 'Title and message are required.')
        return redirect('admin_broadcast')
    return render(request, 'admin_panel/broadcast.html')
