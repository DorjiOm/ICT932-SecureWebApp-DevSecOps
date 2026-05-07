from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
from io import BytesIO
import base64
from .models import Profile

# Register a new user
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created! Please set up 2FA.')
            return redirect('setup_2fa')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login existing user
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Check if user has 2FA set up
            if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
                return redirect('verify_2fa')
            # Redirect admin to admin dashboard, users to task list
            if user.profile.is_admin():
                return redirect('admin_dashboard')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout user
def logout_view(request):
    logout(request)
    return redirect('login')

# Setup 2FA - generates QR code
@login_required
def setup_2fa(request):
    user = request.user

    # Reuse existing unconfirmed device or create new one
    device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        device = TOTPDevice.objects.create(
            user=user,
            name='Google Authenticator',
            confirmed=False
        )

    # Generate QR code
    otp_url = device.config_url
    qr = qrcode.make(otp_url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    if request.method == 'POST':
        token = request.POST.get('token')
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            messages.success(request, '2FA setup complete!')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/setup_2fa.html', {'qr_code': qr_code})

# Verify 2FA token during login
@login_required
def verify_2fa(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        if device and device.verify_token(token):
            request.session['otp_verified'] = True
            if request.user.profile.is_admin():
                return redirect('admin_dashboard')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid code. Please try again.')
    return render(request, 'accounts/verify_2fa.html')

# Admin dashboard
@login_required
def admin_dashboard(request):
    if not request.user.profile.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('task_list')
    from tasks.models import Tas