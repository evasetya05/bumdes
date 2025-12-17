from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '192.168.1.102', 'localhost']
CSRF_TRUSTED_ORIGINS = ['https://*.preview.app.github.dev']


import pymysql
pymysql.install_as_MySQLdb()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bumdes',
        'USER': 'eva',
        'PASSWORD': 'toor',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
    }
}
