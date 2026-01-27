from .base import *

DEBUG = False

# URL configuration
ROOT_URLCONF = 'bumdes.urls'

ALLOWED_HOSTS = ['bumdessumberoto.teknusa.com', 'www.bumdessumberoto.teknusa.com']
CSRF_TRUSTED_ORIGINS = ['https://bumdessumberoto.teknusa.com', 'https://www.bumdessumberoto.teknusa.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'teknusas_bumdes_sumberoto',
        'USER': 'teknusas_bumdes_sumberoto',
        'PASSWORD': '@Sumberoto123',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
