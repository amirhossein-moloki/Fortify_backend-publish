from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&y@xqt2dm&)f%ul$#(andc)-_kpjsc9115zv476xh*@ll-z=lz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'rest_framework',  # برای Django REST Framework
    'rest_framework_simplejwt',  # برای JWT
    'corsheaders',  # اضافه کردن corsheaders
    'channels',
    'chats',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # اضافه کردن CorsMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'Fortify_back.urls'

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


ASGI_APPLICATION ='Fortify_back.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# JWT Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/min',
        'user': '10/min',
        'custom_scope': '20/hour',  # نرخ خاص برای یک ویو خاص
    }
}

# JWT Token Expiry Time Settings (Optional)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # مدت زمان اعتبار توکن دسترسی
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # مدت زمان اعتبار توکن بازنشانی
    'ROTATE_REFRESH_TOKENS': False,                   # چرخش توکن‌های بازنشانی
    'BLACKLIST_AFTER_ROTATION': False,                # مسدودسازی توکن‌های بازنشانی بعد از چرخش
    'ALGORITHM': 'HS256',                             # الگوریتم رمزنگاری
    'SIGNING_KEY': SECRET_KEY,                        # کلید امضای JWT
    'VERIFYING_KEY': None,                            # کلید تایید JWT (مربوط به امضا در سرور)
    'AUDIENCE': None,                                 # مخاطب
    'ISSUER': None,                                   # صادرکننده
}

# User model settings
AUTH_USER_MODEL = 'accounts.User'

CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOW_CREDENTIALS = True  # اجازه دادن به کوکی‌ها و اعتبارنامه‌ها
CORS_ALLOW_METHODS = [
    'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS',
]
CORS_ALLOW_HEADERS = [
    'content-type', 'accept', 'Authorization', 'X-Requested-With', 'Access-Control-Allow-Origin',
]


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True  # استفاده از SSL
EMAIL_USE_TLS = False  # باید False باشد چون SSL استفاده می‌کنید
EMAIL_HOST_USER = 'amir.moloki8558@gmail.com'  # ایمیل شما
EMAIL_HOST_PASSWORD = 'drgzueqzrcupbfyr'  # رمز عبور ایمیل
DEFAULT_FROM_EMAIL = 'amir.moloki8558@gmail.com'
