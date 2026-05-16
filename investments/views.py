from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import InvestmentPlan, Investment
from transactions.models import Transaction
from notifications.models import Notification


@login_required
def dashboard(request):
    user = request.user
    active_investments = Investment.objects.filter(user=user, status='active')
    recent_transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:5]
    plans = InvestmentPlan.objects.filter(is_active=True)
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]

    # Chart data for earnings (last 7 days)
    from django.db.models import Sum
    from django.db.models.functions import TruncDate
    from datetime import date, timedelta as td
    labels = []
    profits = []
    for i in range(6, -1, -1):
        d = date.today() - td(days=i)
        labels.append(d.strftime('%b %d'))
        daily = Transaction.objects.filter(
            user=user, transaction_type='profit',
            created_at__date=d
        ).aggregate(total=Sum('amount'))['total'] or 0
        profits.append(float(daily))

    context = {
        'active_investments': active_investments,
        'recent_transactions': recent_transactions,
        'plans': plans,
        'notifications': notifications,
        'chart_labels': labels,
        'chart_profits': profits,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def invest_view(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, is_active=True)
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        user = request.user

        if amount < plan.min_deposit:
            messages.error(request, f'Minimum investment is ${plan.min_deposit}')
            return redirect('invest', plan_id=plan_id)
        if amount > plan.max_deposit:
            messages.error(request, f'Maximum investment is ${plan.max_deposit}')
            return redirect('invest', plan_id=plan_id)
        if user.wallet_balance < amount:
            messages.error(request, 'Insufficient wallet balance. Please deposit funds first.')
            return redirect('deposit')

        # Deduct from wallet
        user.wallet_balance -= amount
        user.save()

        # Calculate end date
        unit = plan.duration_unit
        duration = plan.duration
        if unit == 'hours':
            end = timezone.now() + timedelta(hours=duration)
        elif unit == 'days':
            end = timezone.now() + timedelta(days=duration)
        elif unit == 'weeks':
            end = timezone.now() + timedelta(weeks=duration)
        else:
            end = timezone.now() + timedelta(days=duration * 30)

        investment = Investment.objects.create(
            user=user, plan=plan, amount=amount, expected_end=end
        )

        Transaction.objects.create(
            user=user, transaction_type='investment',
            amount=amount, status='completed',
            description=f'Investment in {plan.name} plan'
        )

        Notification.objects.create(
            user=user,
            title='Investment Activated',
            message=f'Your ${amount} investment in {plan.name} plan is now active. Expected profit: ${investment.get_expected_profit()}'
        )

        messages.success(request, f'Successfully invested ${amount} in {plan.name}!')
        return redirect('my_investments')

    return render(request, 'dashboard/invest.html', {'plan': plan})


@login_required
def my_investments(request):
    investments = Investment.objects.filter(user=request.user)
    return render(request, 'dashboard/my_investments.html', {'investments': investments})


@login_required
def plans_view(request):
    plans = InvestmentPlan.objects.filter(is_active=True)
    return render(request, 'dashboard/plans.html', {'plans': plans})
