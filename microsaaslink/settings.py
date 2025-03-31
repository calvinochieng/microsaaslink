from pathlib import Path
from django.contrib.messages import constants as messages

from decouple import config, Csv
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')


DEBUG =  config('DEBUG',  cast=bool)
LOCAL = False

PRODUCTION_MODE = config('PRODUCTION_MODE',cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
   
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'cloudinary_storage',
    'cloudinary',
    # Local Apps
    'app',
]


MESSAGE_TAGS = {
    messages.DEBUG: 'is-info',
    messages.INFO: 'is-info',
    messages.SUCCESS: 'is-success',
    messages.WARNING: 'is-warning',
    messages.ERROR: 'is-danger',
}

# Authentication Settings
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'

# Allauth configuration
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {'email'}

# Don't redirect to the verification page after signup
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/dashboard/'

# If you want to automatically redirect to dashboard after email confirmation
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/dashboard/'

# This will make sure users are redirected to the dashboard after login
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True



SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
          'profile',
          'email'
        ],
        'AUTH_PARAMS': { "access_type": "online"}
        ,
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_SECRET_KEY'),
            'key': ''
        }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.contrib.auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

ACCOUNT_LOGIN_ON_GET = True

CLOUDINARY_STORAGE = {
            'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
            'API_KEY': config('CLOUDINARY_API_KEY'),
            'API_SECRET': config('CLOUDINARY_API_SECRET'),
        } 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',#WhiteNOISE ADDED
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'microsaaslink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  [
            'templates'
        ],
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

WSGI_APPLICATION = 'microsaaslink.wsgi.application'

if LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres.hdfxpccuiixjkdtepxle',
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': 'aws-0-eu-central-1.pooler.supabase.com',
            'PORT': '5432',
            'OPTIONS': {
                'sslmode': 'require',
            }
        }
    }
    # print("databases", DATABASES)



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
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# STATIC FILE SETUP
STATICFILES_DIRS = [BASE_DIR / 'static/']
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = '/static/'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/' 
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'     


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
