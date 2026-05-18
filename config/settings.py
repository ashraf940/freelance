import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

DEBUG = True
ALLOWED_HOSTS = ['*']


# ========================
# APPS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'ckeditor',
    'phonenumber_field',
    'django_countries',
    'axes',
    'constance',
    'constance.backends.database',

    # local apps
    'accounts',
    'gigs',
    'jobs',
    'orders',
    'payments',
    'reviews',
    'chat',
    'notifications',
    'analytics',
    'subscriptions',
    'adminpanel',
    'ai',
    'security',
    'gamification',
    'channels',
    'blog',
    # 'ckeditor',
]
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}


# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]


ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'


# ========================
# DATABASE
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ========================
# AUTH
# ========================
AUTH_USER_MODEL = 'accounts.User'


# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# INTERNATIONALIZATION
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ========================
# STATIC / MEDIA
# ========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ========================
# REST FRAMEWORK
# ========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# ========================
# JWT
# ========================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ========================
# EMAIL
# ========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# ========================
# AXES (FIXED)
# ========================
AXES_ENABLED = False
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# ========================
# CACHE (IMPORTANT FIX)
# ========================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique",
    }
}


# ========================
# RATELIMIT (DISABLED SAFE)
# ========================
RATELIMIT_ENABLE = False


# ========================
# CONSTANCE
# ========================
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'SITE_NAME': ('Freelance Platform', 'Website name'),
    'PLATFORM_COMMISSION': (10, 'Commission percentage', int),
    'MIN_WITHDRAWAL': (500, 'Minimum withdrawal amount', int),
}


LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Optional: path to your project templates
        'APP_DIRS': True,  # This allows Django to find templates in installed apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "fitcal682@gmail.com"
EMAIL_HOST_PASSWORD = "xcfs whmi wfxd apdb"  # ⚠️ Ye Gmail ka App Password hoga
DEFAULT_FROM_EMAIL = "FitCal <fitcal682@gmail.com>"



CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # For development
        # For production use Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [("127.0.0.1", 6379)],
        # },
    },
}

ASGI_APPLICATION = 'config.asgi.application'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


import os
from pathlib import Path

# Static files configuration (Django templates ke liye zaroori hai)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Agar aap whitenoise use karna chahein static files ke liye (Recommended):
# pip install whitenoise aur usko MIDDLEWARE me 'django.middleware.security.SecurityMiddleware' ke foran baad add karen:
# 'whitenoise.middleware.WhiteNoiseMiddleware',

# Allowed Hosts aur Debug setting
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*'] # Railway ka domain automatic handle karne ke liye, baad me specific bhi kar sakte hain