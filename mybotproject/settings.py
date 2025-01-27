
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'something-secret-dev')
DEBUG = (os.getenv('DJANGO_DEBUG', 'True') == 'True')

ALLOWED_HOSTS = ['www.bale.medogram.ir', 'bale.medogram.ir', 'https://bale.medogram.ir']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'auth_bot',
    'kavenegar',
    'rest_framework_simplejwt',
]

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=28800),  # عمر توکن دسترسی
    'REFRESH_TOKEN_LIFETIME': timedelta(days=100),  # عمر توکن تازه‌سازی
    'ROTATE_REFRESH_TOKENS': True,  # توکن تازه‌سازی قدیمی را غیرفعال می‌کند
    'BLACKLIST_AFTER_ROTATION': True,  # امکان اضافه کردن توکن به لیست سیاه پس از دوران
    'ALGORITHM': 'HS256',  # الگوریتم رمزنگاری
    'SIGNING_KEY': SECRET_KEY,  # کلید امضای JWT
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),  # نوع هدر JWT
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# یا برای اجازه دادن به همه دامنه‌ها:
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'x-csrftoken',
    'accept'
]

ROOT_URLCONF = 'mybotproject.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'mybotproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
 }

TALKBOT_API_KEY = os.getenv('TALKBOT_API_KEY', '')
KAVEH_NEGAR_API_KEY = os.getenv('KAVEH_NEGAR_API_KEY', '')
BALE_BOT_TOKEN = os.getenv('BALE_BOT_TOKEN', '')
