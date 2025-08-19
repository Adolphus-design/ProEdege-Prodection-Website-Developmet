import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-q)3@9gh_m@lff88ry*v!ih#1%3!h!h5$!@*b(n(rw)i^h@sy#m'

DEBUG = True

ALLOWED_HOSTS = [
    'proedegeproperty.onrender.com',
    'www.proedegeproperty.onrender.com',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'proedge',
    'listings',
    #'staff',
    'adminpanel',
    'agencylistings',
    'bankdashboard',
    'cloudinary',
    'cloudinary_storage',
    #'widget_tweaks',
    'agent'
]

# Cloudinary configuration (replace with your real credentials)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dhhmoioij',
    'API_KEY': '547473313418333',
    'API_SECRET': 'XNdrSAugmeHTxE-bDUoPj10PJIs',
}

# Use Cloudinary for media file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Efficient static files serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA settings removed to use Cloudinary instead (do NOT define MEDIA_ROOT or MEDIA_URL here)

# Custom user model
AUTH_USER_MODEL = 'proedge.CustomUser'

# Authentication redirects
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = 'login'

# Email backend configuration
"""EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kamogelotshehla@gmail.com'
EMAIL_HOST_PASSWORD = 'rorsmoxjwmmfkolq'
DEFAULT_FROM_EMAIL = 'kamogelotshehla@gmail.com'"""


# Email settings for local development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# This is the email address that will appear in the "From" field
DEFAULT_FROM_EMAIL = "no-reply@proedge.local"

