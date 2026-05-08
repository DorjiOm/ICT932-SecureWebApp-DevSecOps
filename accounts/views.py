from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
from io import BytesIO
import base64
import logging
from .models import Profile

# Security: Set up logging for security events
logger = logging.getLogger('security')

# Security: Maximum failed login attempts before lockout
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes in seconds

# Register a new user
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Security: Log successful registration
            logger.info(f'New user registered: {user.username} from IP {request.META.get("REMOTE_ADDR")}')
            login(request, user)
            messages.success(request, 'Account created! Please set up 2FA.')
            return redirect('setup_2fa')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login existing user with brute force protection
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        ip_address = request.META.get('REMOTE_ADDR')

        # Security: Check if account is locked
        cache_key = f'login_attempts_{username}_{ip_address}'
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            # Security: Log lockout event
            logger.warning(f'Account locked: {username} from IP {ip_address} - too many failed attempts')
            messages.error(request, 'Account locked due to too many failed attempts. Try again in 5 minutes.')
            return render(request, 'accounts/login.html', {'form': AuthenticationForm()})

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Security: Reset failed attempts on successful login
            cache.delete(cache_key)
            # Security: Log successful login
            logger.info(f'Successful login: {username} from IP {ip_address}')
            login(request, user)
            if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
                return redirect('verify_2fa')
            if user.profile.is_admin():
                return redirect('admin_dashboard')
            return redirect('task_list')
        else:
            # Security: Increment failed login attempts
            cache.set(cache_key, attempts + 1, LOCKOUT_TIME)
            remaining = MAX_LOGIN_ATTEMPTS - (attempts + 1)
            # Security: Log failed login attempt
            logger.warning(f'Failed login attempt: {username} from IP {ip_address} - {attempts + 1} attempts')
            if remaining > 0:
                messages.error(request, f'Invalid credentials. {remaining} attempts remaining.')
            else:
                messages.error(request, 'Account locked due to too many failed attempts. Try again in 5 minutes.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout user
def logout_view(request):
    # Security: Log logout event
    logger.info(f'User logged out: {request.user.username}')
    logout(request)
    return redirect('login')

# Setup 2FA - generates QR code
@login_required
def setup_2fa(request):
    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        device = TOTPDevice.objects.create(
            user=user,
            name='Google Authenticator',
            confirmed=False
        )
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
            # Security: Log 2FA setup
            logger.info(f'2FA enabled for user: {user.username}')
            messages.success(request, '2FA setup complete!')
            return redirect('task_list')
        else:
            # Security: Log failed 2FA attempt
            logger.warning(f'Failed 2FA setup attempt for user: {user.username}')
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
            # Security: Log successful 2FA verification
            logger.info(f'2FA verified for user: {request.user.username}')
            if request.user.profile.is_admin():
                return redirect('admin_dashboard')
            return redirect('task_list')
        else:
            # Security: Log failed 2FA verification
            logger.warning(f'Failed 2FA verification for user: {request.user.username}')
            messages.error(request, 'Invalid code. Please try again.')
    return render(request, 'accounts/verify_2fa.html')

# Admin dashboard
@login_required
def admin_dashboard(request):
    if not request.user.profile.is_admin():
        # Security: Log unauthorized access attempt
        logger.warning(f'Unauthorized admin access attempt by: {request.user.username}')
        messages.error(request, 'Access denied. Admins only.')
        return redirect('task_list')
    from tasks.models import Task
    from django.contrib.auth.models import User
    all_tasks = Task.objects.all().order_by('user', '-created_at')
    all_users = User.objects.all()
    return render(request, 'accounts/admin_dashboard.html', {
        'all_tasks': all_tasks,
        'all_users': all_users
    })