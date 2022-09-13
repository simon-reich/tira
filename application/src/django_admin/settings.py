"""
Django settings for django_admin project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import logging
from pathlib import Path
import os
import yaml

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

custom_settings = {}
for cfg in (BASE_DIR / "config").glob("*.yml"):
    custom_settings.update(yaml.load(open(cfg, "r").read(), Loader=yaml.FullLoader))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = custom_settings.get("django_secret", 'not-so-secret')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = custom_settings.get("debug", True)
ALLOWED_HOSTS = custom_settings.get("allowed_hosts", [])

TIRA_ROOT = Path(custom_settings.get("tira_root", BASE_DIR.parents[1] / "model" / "src"))
if not TIRA_ROOT.is_dir():
    logging.warning(f"{TIRA_ROOT} does not exists and will be created now.")

(TIRA_ROOT / "state").mkdir(parents=True, exist_ok=True)

DEPLOYMENT = custom_settings.get("deployment", "legacy")
LEGACY_USER_FILE = Path(custom_settings.get("legacy_users_file", TIRA_ROOT / "model" / "users" / "users.prototext"))
DISRAPTOR_SECRET_FILE = Path(custom_settings.get("disraptor_secret_file", "/etc/discourse/client-api-key"))
HOST_GRPC_PORT = custom_settings.get("host_grpc_port", "50051")
APPLICATION_GRPC_PORT = custom_settings.get("application_grpc_port", "50052")
GRPC_HOST = custom_settings.get("grpc_host", "local")  # can be local or remote
TIRA_DB_NAME = Path(TIRA_ROOT / "state") / f"{custom_settings['database'].get('name', 'tira')}.sqlite3" \
    if custom_settings['database'].get('engine', 'django.db.backends.sqlite3') == 'django.db.backends.sqlite3' \
    else custom_settings['database'].get('name', 'tira')
TIRA_DB = {
    'ENGINE': custom_settings['database'].get('engine', 'django.db.backends.sqlite3'),
    'NAME': TIRA_DB_NAME,
    'USER': custom_settings['database'].get('user', 'tira'),
    'PASSWORD': custom_settings['database'].get('password', 'replace-with-db-password'),
    'HOST': custom_settings['database'].get('host', 'tira-mariadb'),
    'PORT': int(custom_settings['database'].get('port', 3306)),
    'TEST': {
        'NAME': "test_tira",
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
# Application definition

INSTALLED_APPS = [
    'tira.apps.TiraConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webpack_loader',
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

ROOT_URLCONF = 'django_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'django_admin.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': TIRA_DB
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


def logger_config(log_dir: Path):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'default': {
                'format': '{levelname} {asctime} {module}: {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'ceph_django_debug': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filters': ['require_debug_true'],
                'filename': log_dir / 'django-debug.log',
                'formatter': 'default'
            },
            'ceph_django_info': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'django-info.log',
                'formatter': 'default'
            },
            'ceph_django_warn': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'django-warning.log',
                'formatter': 'default'
            },
            'ceph_tira_debug': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filters': ['require_debug_true'],
                'filename': log_dir / 'tira-debug.log',
                'formatter': 'default'
            },
            'ceph_tira_info': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'tira-info.log',
                'formatter': 'default'
            },
            'ceph_tira_warn': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'tira-warning.log',
                'formatter': 'default'
            },
            'ceph_tira_db': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'tira-db.log',
                'formatter': 'default'
            },
            'ceph_grpc_debug': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filters': ['require_debug_true'],
                'filename': log_dir / 'grpc-debug.log',
                'formatter': 'default'
            },
            'ceph_grpc_info': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'grpc-info.log',
                'formatter': 'default'
            },
            'ceph_grpc_warn': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': log_dir / 'grpc-warning.log',
                'formatter': 'default'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'ceph_django_debug', 'ceph_django_warn', 'ceph_django_info'],
                'propagate': True,
            },
            'django.requests': {
                'handlers': ['console', 'ceph_django_debug', 'ceph_django_warn', 'ceph_django_info'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['console', 'ceph_django_debug', 'ceph_django_warn', 'ceph_django_info'],
                'propagate': True,
            },
            'tira': {
                'handlers': ['console', 'ceph_tira_debug', 'ceph_tira_warn', 'ceph_tira_info'],
                'propagate': True,
            },
            'tira_db': {
                'handlers': ['console', 'ceph_tira_db'],
                'propagate': True,
            },
            'grpc_server': {
                'handlers': ['console', 'ceph_grpc_debug', 'ceph_grpc_warn', 'ceph_grpc_info'],
                'propagate': True,
            },
        }
    }

# Git Integration
GIT_CI_SERVER_HOST = custom_settings.get('GIT_CI_SERVER_HOST', 'git.webis.de')
GIT_PRIVATE_TOKEN = custom_settings['GIT_PRIVATE_TOKEN']
GIT_USER_NAME = custom_settings['GIT_USER_NAME']
GIT_USER_PASSWORD = custom_settings['GIT_USER_PASSWORD']
GIT_USER_REPOSITORY_NAMESPACE_ID = int(custom_settings.get('GIT_USER_REPOSITORY_NAMESPACE_ID', '146'))
GIT_REGISTRY_PREFIX = custom_settings.get('GIT_REGISTRY_PREFIX', 'registry.webis.de/code-research/tira')
GIT_USER_REPOSITORY_BRANCH = custom_settings.get('GIT_USER_REPOSITORY_BRANCH', 'main')
GIT_CONTAINER_REGISTRY_HOST = custom_settings.get('GIT_CONTAINER_REGISTRY_HOST', 'registry.webis.de')
GIT_CI_AVAILABLE_RESOURCES = {
    'small-resources': {'cores': 2, 'ram': 10, 'description': 'Small (2 CPU Cores, 10GB of RAM)', 'key': 'small-resources'},
    'large-resources': {'cores': 8, 'ram': 40, 'description': 'Large (8 CPU Cores, 40GB of RAM)', 'key': 'large-resources'},
}

# Logging
ld = Path(custom_settings.get("logging_dir", TIRA_ROOT / "log" / "tira-application"))
try:
    ld.mkdir(parents=True, exist_ok=True)
except PermissionError as e:
    print(f"failed to create logging path {ld}: ", e)
if os.access(ld, os.W_OK):
    LOGGING = logger_config(ld)
else:
    print(f"failed to initialize logging in {ld}")
    if DEBUG:
        print(f"Logging to {BASE_DIR}")
        LOGGING = logger_config(Path(BASE_DIR))
    else:
        raise PermissionError(f"Can not write to {ld} in production mode.")


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/public/'

STATICFILES_DIRS = [
    BASE_DIR / "static/",
    BASE_DIR / "tira/static/"
]

STATIC_ROOT = "/var/www/public"

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': DEBUG,
        'BUNDLE_DIR_NAME': '/bundles/',
        'STATS_FILE': BASE_DIR / 'tira' / 'frontend' / 'webpack-stats.json'
    }
}
