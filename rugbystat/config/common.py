import os
from os.path import join

from configurations import Configuration, values

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Common(Configuration):

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third party apps
        'rest_framework',
        'rest_framework.authtoken',  # token authentication
        'django_rq',                 # asynchronous queuing
        'versatileimagefield',       # image manipulation
        'django_dropbox',

        # Your apps
        'authentication',
        'users'

    )

    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/
    MIDDLEWARE = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware'
    )

    ROOT_URLCONF = 'urls'

    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'Not a secret')
    WSGI_APPLICATION = 'wsgi.application'

    # Email
    EMAIL_BACKEND = values.Value('django.core.mail.backends.smtp.EmailBackend')

    ADMINS = (
        ('Author', 'ultrasnet@mail.ru'),
    )

    # Postgres
    DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
    DB_PASS = os.environ.get('POSTGRES_PASS', '1111')
    DB_URL = 'postgres://{}:{}@localhost/rugbystat'.format(DB_USER, DB_PASS)
    DATABASES = values.DatabaseURLValue(DB_URL)

    # General
    APPEND_SLASH = values.BooleanValue(False)
    TIME_ZONE = 'Europe/Moscow'
    LANGUAGE_CODE = 'ru-ru'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'

    # Static Files
    STATIC_ROOT = join(os.path.dirname(BASE_DIR), '../static_root')
    STATICFILES_DIRS = [join(os.path.dirname(BASE_DIR), 'static'), ]
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), '../media_root')
    MEDIA_URL = '/media/'

    DROPBOX_ACCESS_TOKEN = 'aqY2g6XyAaQAAAAAAAA22jImVcWLjm052Cp8xzQjx2b5F255QK08Ql2iPUGzpQg0'
    DEFAULT_FILE_STORAGE = 'django_dropbox.storage.DropboxStorage'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [STATICFILES_DIRS],
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages'
                ],
                'loaders':[
                    ('django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]),
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = values.BooleanValue(False)
    for config in TEMPLATES:
        config['OPTIONS']['debug'] = DEBUG

    # Password Validation
    # https://docs.djangoproject.com/en/1.10/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 9,
            }
        },
    ]

    # Logging
    from .logging import LOGGING

    # Custom user app
    AUTH_USER_MODEL = 'users.User'

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS':
            'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 10)),
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        )
    }

    # Versatile Image Field
    VERSATILEIMAGEFIELD_SETTINGS = {
        # The amount of time, in seconds, that references to created images
        # should be stored in the cache. Defaults to `2592000` (30 days)
        'cache_length': 2592000,
        'cache_name': 'versatileimagefield_cache',
        'jpeg_resize_quality': 70,
        'sized_directory_name': '__sized__',
        'filtered_directory_name': '__filtered__',
        'placeholder_directory_name': '__placeholder__',
        'create_images_on_demand': False
    }

    # django-rq
    # Adds dashboard link for queues in /admin, This will override the default
    # admin template so it may interfere with other apps that modify the
    # default admin template. If you're using such an app, simply remove this.
    RQ_SHOW_ADMIN_LINK = True
