import pymysql
pymysql.install_as_MySQLdb()

import os
from pathlib import Path
import dj_database_url
from urllib.parse import urlparse
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY SETTINGS
# -----------------------------

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'vr123456')

# Allow all hosts if ALLOWED_HOSTS is not set
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else ['*']

# -----------------------------
# APPLICATION DEFINITION
# -----------------------------

INSTALLED_APPS = [
    'bethany_church',
    'attendance',
    'ministry',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'schedule',
    'crispy_forms',	
    'crispy_bootstrap5',
    'widget_tweaks',
    'storages',  # Added for django-storages
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added for static file handling
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bethany_church.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by Allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bethany_church.wsgi.application'

# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------

# Parse database configuration from $JAWSDB_URL
DATABASE_URL = os.getenv('JAWSDB_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Default to local MySQL if JAWSDB_URL is not set (useful for local development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'it7wrdzo6w9tdmjd',
            'USER': 'pabi4xxteo7vc8ow',
            'PASSWORD': 'clw8fwjcbz3yjv8v',
            'HOST': 'co28d739i4m2sb7j.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
            'PORT': '3306',
        }
    }

# -----------------------------
# AUTHENTICATION SETTINGS
# -----------------------------

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/admin_home/'
LOGOUT_REDIRECT_URL = 'login'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# -----------------------------
# LOGGING CONFIGURATION
# -----------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.template': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# -----------------------------
# STATIC FILES CONFIGURATION
# -----------------------------

STATIC_URL = '/static/'

# The directory where collectstatic will collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional directories to look for static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Use WhiteNoise to serve static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -----------------------------
# MEDIA FILES CONFIGURATION
# -----------------------------

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Bucketeer (S3-Compatible) Configuration
AWS_ACCESS_KEY_ID = os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('BUCKETEER_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('BUCKETEER_S3_ENDPOINT_URL')  # Example: 'https://s3.amazonaws.com'
AWS_S3_REGION_NAME = os.getenv('BUCKETEER_S3_REGION_NAME')  # Example: 'us-east-1'

# If Bucketeer provides a custom domain, set it here
# Otherwise, it will default to the endpoint URL
AWS_S3_CUSTOM_DOMAIN = os.getenv('BUCKETEER_S3_CUSTOM_DOMAIN', f"{AWS_STORAGE_BUCKET_NAME}.{urlparse(AWS_S3_ENDPOINT_URL).hostname}")

# Optional: Set default ACL. 'public-read' allows public access to files.
AWS_DEFAULT_ACL = 'public-read'

# Optional: URL that handles the media served from S3
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# -----------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# -----------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
