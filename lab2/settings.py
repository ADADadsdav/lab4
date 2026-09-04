import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv('APP_ENV', os.getenv('NODE_ENV', 'development')).lower()

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if APP_ENV == 'production':
        raise ImproperlyConfigured('SECRET_KEY must be set in production')
    SECRET_KEY = secrets.token_urlsafe(50)

DEBUG = os.getenv('DEBUG', 'true' if APP_ENV != 'production' else 'false').lower() in {'1', 'true', 'yes'}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'postgres', 'testserver']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'movies.apps.MoviesConfig',
    'users.apps.UsersConfig',
    'custom_auth.apps.CustomAuthConfig',
    'rest_framework',
    'drf_spectacular',
]
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'custom_auth.middleware.AuthenticationMiddleware',

]

ROOT_URLCONF = 'lab2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
            ],
        },
    },
]

WSGI_APPLICATION = 'lab2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases




DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {'default': {'ENGINE': DB_ENGINE, 'NAME': os.getenv('DB_NAME', str(BASE_DIR / 'db.sqlite3'))}}
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.getenv("DB_NAME"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
            'HOST': os.getenv("DB_HOST"),
            'PORT': os.getenv("DB_PORT"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['custom_auth.permissions.CookieAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'custom_auth.exceptions.custom_exception_handler',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Movie API',
    'DESCRIPTION': (
        'REST API лабораторных работ №2–4: аутентификация JWT в HttpOnly Cookies, '
        'CRUD фильмов, OAuth 2.0 через Яндекс и мягкое удаление.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'CookieAuth': {
                'type': 'apiKey',
                'in': 'cookie',
                'name': 'access_token',
                'description': 'JWT access token in the HttpOnly access_token cookie.',
            },
            'YandexOAuth2': {
                'type': 'oauth2',
                'description': 'OAuth 2.0 Authorization Code flow через Яндекс.',
                'flows': {
                    'authorizationCode': {
                        'authorizationUrl': 'https://oauth.yandex.ru/authorize',
                        'tokenUrl': 'https://oauth.yandex.ru/token',
                        'scopes': {'login:info': 'Получение информации о пользователе'},
                    }
                },
            }
        }
    },
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayRequestDuration': True,
    },
}
JWT_ACCESS_SECRET = os.getenv('JWT_ACCESS_SECRET')
JWT_REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET')
JWT_ACCESS_EXPIRATION = int(os.getenv('JWT_ACCESS_EXPIRATION', 900))
JWT_REFRESH_EXPIRATION = int(os.getenv('JWT_REFRESH_EXPIRATION', 604800))

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@example.com')

# OAuth Settings
YANDEX_CLIENT_ID = os.getenv('YANDEX_CLIENT_ID')
YANDEX_CLIENT_SECRET = os.getenv('YANDEX_CLIENT_SECRET')
YANDEX_CALLBACK_URL = os.getenv('YANDEX_CALLBACK_URL')
# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
