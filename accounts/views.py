from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from referrals.models import Referral
import uuid


def register_view(request):
    ref_code = request.GET.get('ref', '')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # Handle referral
            ref = request.POST.get('referral_code', '')
            if ref:
                try:
                    referrer = User.objects.get(referral_code=ref)
                    user.referred_by = referrer
                    user.save()
                    Referral.objects.create(referrer=referrer, referred=user)
                except User.DoesNotExist:
                    pass
            login(request, user)
            messages.success(request, f'Welcome to CryptoVest, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm(initial={'referral_code': ref_code})
    return render(request, 'auth/register.html', {'form': form, 'ref_code': ref_code})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                if user.is_banned:
                    messages.error(request, 'Your account has been suspended. Contact support.')
                    return render(request, 'auth/login.html', {'form': form})
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'dashboard/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dashboard/change_password.html', {'form': form})


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # In production, send email with token
            messages.success(request, 'Password reset instructions sent to your email.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'auth/password_reset.html')
