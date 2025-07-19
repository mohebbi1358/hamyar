import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from datetime import timedelta

# بارگذاری متغیرهای محیطی از .env فقط در لوکال
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# محیط پروژه
ENVIRONMENT = os.getenv('DJANGO_ENV', 'local')

# کلید مخفی
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'unsafe-default-secret-key')

# دیباگ
DEBUG = ENVIRONMENT != 'production'

ALLOWED_HOSTS = ['*']

# اپلیکیشن‌ها
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # اپ‌های پروژه
    'accounts',
    'main',
    'martyrs',
    'donation',
    'wallet',
    'news',
    'common',
    'eternals',
    'notification',

    # سایر اپ‌ها
    'rest_framework',
    'django_extensions',
]

# میدلورها
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # برای استاتیک‌ها در پروداکشن
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# قالب‌ها
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# دیتابیس
if ENVIRONMENT == 'production':
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'hamyar_db',
            'USER': 'hamyar_user',
            'PASSWORD': 'Hamyar123!',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }

# احراز هویت
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# زبان و زمان
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# فایل‌های استاتیک
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# فایل‌های مدیا
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#MEDIA_ROOT = BASE_DIR / 'media'

# مدل کاربر سفارشی
AUTH_USER_MODEL = 'accounts.User'

# تنظیمات DRF و JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# سایر تنظیمات خاص
MELI_PAYAMAK_USERNAME = '9309167146'
MELI_PAYAMAK_PASSWORD = '717008bf-8c0b-49ad-a595-44eb41817cde'
MELI_PAYAMAK_SENDER = '3000700642'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
