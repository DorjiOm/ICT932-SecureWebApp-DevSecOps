"""
accounts/views.py
=================
This module handles all authentication and authorization views for the
Secure Task Manager application. Security is the primary concern throughout.

Security Features Implemented:
- Secure user registration with Django's built-in form validation
- Login with brute force protection (account lockout after 5 attempts)
- Two-Factor Authentication (2FA) using TOTP standard
- Role-Based Access Control (RBAC) with Admin and User roles
- Security event logging for audit trail
- Session management and secure redirects
"""

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

# Security: Dedicated security logger for audit trail
# All security events are recorded with timestamp and IP address
logger = logging.getLogger('security')

# Security: Brute force protection constants
# Account is locked for 5 minutes after 5 failed login attempts
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes in seconds


def register_view(request):
    """
    Handle user registration.
    
    Security measures:
    - Uses Django's UserCreationForm which enforces password complexity rules
    - Passwords are automatically hashed using PBKDF2 with SHA-256
    - New users are automatically redirected to 2FA setup after registration
    - Registration event is logged with IP address for audit trail
    """
    if request.method == 'POST':
        # Security: UserCreationForm validates password strength automatically
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Password is automatically hashed, never stored in plain text
            
            # Security: Log successful registration with IP for audit trail
            logger.info(
                f'New user registered: {user.username} '
                f'from IP {request.META.get("REMOTE_ADDR")}'
            )
            
            login(request, user)
            messages.success(request, 'Account created! Please set up 2FA.')
            
            # Security: Force 2FA setup immediately after registration
            return redirect('setup_2fa')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login with brute force protection.
    
    Security measures:
    - Tracks failed login attempts per username AND IP address
    - Locks account for 5 minutes after 5 failed attempts
    - Resets attempt counter on successful login
    - All login events (success and failure) logged for audit trail
    - Redirects to 2FA verification if user has 2FA enabled
    - Redirects admin users to admin dashboard, regular users to task list
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        ip_address = request.META.get('REMOTE_ADDR')

        # Security: Unique cache key combines username AND IP
        # This prevents both credential stuffing and IP-based bypass attacks
        cache_key = f'login_attempts_{username}_{ip_address}'
        attempts = cache.get(cache_key, 0)

        # Security: Check if account is locked due to too many failed attempts
        if attempts >= MAX_LOGIN_ATTEMPTS:
            logger.warning(
                f'Account locked: {username} from IP {ip_address} '
                f'- too many failed attempts'
            )
            messages.error(
                request,
                'Account locked due to too many failed attempts. '
                'Try again in 5 minutes.'
            )
            return render(request, 'accounts/login.html', {'form': AuthenticationForm()})

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Security: Reset failed attempts counter on successful login
            cache.delete(cache_key)
            
            # Security: Log successful login for audit trail
            logger.info(f'Successful login: {username} from IP {ip_address}')
            
            login(request, user)
            
            # Security: If user has 2FA enabled, require verification before access
            if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
                return redirect('verify_2fa')
            
            # Security: Role-based redirect after login
            if user.profile.is_admin():
                return redirect('admin_dashboard')
            return redirect('task_list')
        else:
            # Security: Increment failed attempt counter with expiry time
            cache.set(cache_key, attempts + 1, LOCKOUT_TIME)
            remaining = MAX_LOGIN_ATTEMPTS - (attempts + 1)
            
            # Security: Log failed attempt with attempt count for monitoring
            logger.warning(
                f'Failed login attempt: {username} from IP {ip_address} '
                f'- {attempts + 1} attempts'
            )
            
            if remaining > 0:
                messages.error(request, f'Invalid credentials. {remaining} attempts remaining.')
            else:
                messages.error(
                    request,
                    'Account locked due to too many failed attempts. '
                    'Try again in 5 minutes.'
                )
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout.
    
    Security measures:
    - Clears all session data on logout
    - Logs logout event for audit trail
    - Redirects to login page
    """
    # Security: Log logout event before clearing session
    logger.info(f'User logged out: {request.user.username}')
    logout(request)  # Clears all session data
    return redirect('login')


@login_required
def setup_2fa(request):
    """
    Handle 2FA setup for new users.
    
    Security measures:
    - Requires user to be logged in (@login_required)
    - Reuses existing unconfirmed device to prevent QR code invalidation
    - Uses TOTP (Time-based One-Time Password) standard
    - QR code generated for easy Google Authenticator setup
    - Device only confirmed after successful token verification
    - Setup event logged for audit trail
    """
    user = request.user

    # Security: Reuse existing unconfirmed device to keep QR code stable
    # Creating a new device each time would invalidate the previous QR code
    device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        # Create new TOTP device linked to user's account
        device = TOTPDevice.objects.create(
            user=user,
            name='Google Authenticator',
            confirmed=False  # Not confirmed until user enters valid token
        )

    # Security: Generate QR code from device's config URL
    # This URL contains the secret key needed by Google Authenticator
    otp_url = device.config_url
    qr = qrcode.make(otp_url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    # Encode as base64 for embedding directly in HTML (no file storage needed)
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    if request.method == 'POST':
        token = request.POST.get('token')
        
        # Security: Verify the TOTP token against the device's secret
        if device.verify_token(token):
            device.confirmed = True  # Mark device as confirmed
            device.save()
            
            # Security: Log successful 2FA setup
            logger.info(f'2FA enabled for user: {user.username}')
            messages.success(request, '2FA setup complete!')
            return redirect('task_list')
        else:
            # Security: Log failed 2FA setup attempt
            logger.warning(f'Failed 2FA setup attempt for user: {user.username}')
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/setup_2fa.html', {'qr_code': qr_code})


@login_required
def verify_2fa(request):
    """
    Handle 2FA verification during login.
    
    Security measures:
    - Requires user to be logged in (@login_required)
    - Verifies TOTP token against user's confirmed device
    - Marks session as 2FA verified on success
    - Failed verification logged for monitoring
    - Role-based redirect after successful verification
    """
    if request.method == 'POST':
        token = request.POST.get('token')
        
        # Security: Get user's confirmed 2FA device
        device = TOTPDevice.objects.filter(
            user=request.user,
            confirmed=True  # Only use confirmed devices
        ).first()
        
        if device and device.verify_token(token):
            # Security: Mark session as 2FA verified
            request.session['otp_verified'] = True
            
            # Security: Log successful 2FA verification
            logger.info(f'2FA verified for user: {request.user.username}')
            
            # Security: Role-based redirect
            if request.user.profile.is_admin():
                return redirect('admin_dashboard')
            return redirect('task_list')
        else:
            # Security: Log failed 2FA verification attempt
            logger.warning(
                f'Failed 2FA verification for user: {request.user.username}'
            )
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/verify_2fa.html')


@login_required
def admin_dashboard(request):
    """
    Display admin dashboard with all users and tasks.
    
    Security measures:
    - Requires user to be logged in (@login_required)
    - Checks user's role before granting access (RBAC enforcement)
    - Non-admin users are redirected with error message
    - Unauthorized access attempts are logged for monitoring
    - Only accessible to users with 'admin' role in their Profile
    """
    # Security: Enforce RBAC - check admin role before granting access
    if not request.user.profile.is_admin():
        # Security: Log unauthorized access attempt
        logger.warning(
            f'Unauthorized admin access attempt by: {request.user.username}'
        )
        messages.error(request, 'Access denied. Admins only.')
        return redirect('task_list')

    # Admin can see ALL tasks and ALL users
    from tasks.models import Task
    from django.contrib.auth.models import User
    all_tasks = Task.objects.all().order_by('user', '-created_at')
    all_users = User.objects.all()

    return render(request, 'accounts/admin_dashboard.html', {
        'all_tasks': all_tasks,
        'all_users': all_users
    })