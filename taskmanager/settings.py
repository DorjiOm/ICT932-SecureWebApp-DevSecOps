from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security: Secret key should be stored in environment variable in production
SECRET_KEY = 'django-insecure-@)fib_u9m_$nj14=nro0f1+yi@-0fy1qoao45r(tx-)109m(!6'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'csp',
    'accounts',
    'tasks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'taskmanager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'taskmanager.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'

# 2FA Settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/tasks/'

# Security Headers
# Fixes OWASP ZAP findings
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevents MIME sniffing attacks
SECURE_BROWSER_XSS_FILTER = True    # Enables browser XSS protection
X_FRAME_OPTIONS = 'DENY'            # Prevents clickjacking attacks

# Security: Session timeout settings
# Auto logout after 10 minutes of inactivity
SESSION_COOKIE_AGE = 600            # 10 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True   # Reset timer on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Logout when browser closes

# Security: Cookie flags
# Fixes OWASP ZAP Low risk - Cookie No HttpOnly Flag
CSRF_COOKIE_HTTPONLY = True         # Prevent JavaScript access to CSRF cookie
SESSION_COOKIE_HTTPONLY = True      # Prevent JavaScript access to session cookie

# Security: Content Security Policy
# Fixes OWASP ZAP Medium risk - CSP header not set
# Prevents XSS attacks by controlling which resources browsers can load
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],          # Only allow resources from same origin
        "script-src": ["'self'"],           # Only allow scripts from same origin
        "style-src": ["'self'", "'unsafe-inline'"],  # Allow inline styles for Django forms
        "img-src": ["'self'", "data:"],     # Allow images from same origin and data URIs
        "font-src": ["'self'"],             # Only allow fonts from same origin
    }
}

# Security: Logging configuration
# Records all security events with timestamp and IP address
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '[{asctime}] SECURITY {levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'security.log',
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}