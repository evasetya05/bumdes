import os
import sys
from pathlib import Path

import pymysql

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add the apps directories to the Python path
APPS_DIR = os.path.join(BASE_DIR, 'apps')
APPS_MODULES_DIR = os.path.join(APPS_DIR, 'modules')

# Add to Python path if not already there
for path in [APPS_DIR, APPS_MODULES_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

SECRET_KEY = os.getenv('SECRET_KEY', '&9b7(-8cp5)mkz4j8kz*o_%njy944qn1p69ojdz35ui97)_ai8')

ALLOWED_HOSTS = []
CSRF_TRUSTED_ORIGINS = []

INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
 
    # Local apps


    'apps.core',



    'apps.modules.ledger',
    'extras',
    'users',
    
   
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bumdes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.company_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'bumdes.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Authentication settings
LOGIN_URL = 'accounts:login'  # URL name for the login page
LOGIN_REDIRECT_URL = "dashboard"  # URL name of the dashboard page after login
LOGOUT_REDIRECT_URL = "accounts:login"  # Redirect to login page after logout

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_LEDGER_CURRENCY_SYMBOL = 'Rp'
DJANGO_LEDGER_SPACED_CURRENCY_SYMBOL = True

CKEDITOR_UPLOAD_PATH = "uploads/"


LANGUAGE_CODE = 'id'

# Gunakan format tanggal Indonesia
DATE_INPUT_FORMATS = ['%d/%m/%Y']
USE_L10N = False
