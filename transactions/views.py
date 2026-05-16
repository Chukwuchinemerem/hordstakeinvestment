from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Transaction, WalletAddress
from notifications.models import Notification


@login_required
def deposit_view(request):
    wallets = WalletAddress.objects.filter(is_active=True)
    crypto_network_pairs = [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "TRC20"),
        ("TON", "TON"),
        ("SOL", "Solana")
    ]
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        crypto = request.POST.get('crypto', 'BTC')
        txn_hash = request.POST.get('txn_hash', '')
        proof = request.FILES.get('proof_image')

        if amount <= 0:
            messages.error(request, 'Invalid amount.')
            return redirect('deposit')

        try:
            wallet = WalletAddress.objects.get(crypto=crypto, is_active=True)
        except WalletAddress.DoesNotExist:
            messages.error(request, 'Selected crypto not available.')
            return redirect('deposit')

        txn = Transaction.objects.create(
            user=request.user,
            transaction_type='deposit',
            amount=amount,
            crypto_currency=crypto,
            txn_hash=txn_hash,
            wallet_address=wallet.address,
            status='pending',
            description=f'Deposit via {crypto}'
        )
        if proof:
            txn.proof_image = proof
            txn.save()

        Notification.objects.create(
            user=request.user,
            title='Deposit Request Submitted',
            message=f'Your deposit of ${amount} via {crypto} is under review. You will be notified once approved.'
        )

        messages.success(request, f'Deposit request submitted! Awaiting admin approval.')
        return redirect('transaction_history')

    return render(request, 'dashboard/deposit.html', {'wallets': wallets, 'crypto_network_pairs': crypto_network_pairs})


@login_required
def withdraw_view(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        crypto = request.POST.get('crypto', 'BTC')
        wallet_address = request.POST.get('wallet_address', '')
        user = request.user

        if amount <= 0:
            messages.error(request, 'Invalid amount.')
            return redirect('withdraw')
        if amount > user.wallet_balance:
            messages.error(request, 'Insufficient balance.')
            return redirect('withdraw')
        if not wallet_address:
            messages.error(request, 'Please provide your wallet address.')
            return redirect('withdraw')

        Transaction.objects.create(
            user=user,
            transaction_type='withdrawal',
            amount=amount,
            crypto_currency=crypto,
            wallet_address=wallet_address,
            status='pending',
            description=f'Withdrawal request via {crypto}'
        )

        # Reserve funds
        user.wallet_balance -= amount
        user.save()

        Notification.objects.create(
            user=user,
            title='Withdrawal Request Submitted',
            message=f'Your withdrawal of ${amount} via {crypto} is being processed.'
        )

        messages.success(request, 'Withdrawal request submitted successfully!')
        return redirect('transaction_history')

    return render(request, 'dashboard/withdraw.html')


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'dashboard/transactions.html', {'transactions': transactions})
