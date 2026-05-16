from django import forms
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input'}))
    referral_code = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-input'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'country', 'avatar', 'btc_wallet', 'eth_wallet', 'usdt_wallet', 'ton_wallet', 'sol_wallet']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'btc_wallet': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'BTC Wallet Address'}),
            'eth_wallet': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ETH Wallet Address'}),
            'usdt_wallet': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'USDT Wallet Address'}),
            'ton_wallet': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'TON Wallet Address'}),
            'sol_wallet': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'SOL Wallet Address'}),
        }
