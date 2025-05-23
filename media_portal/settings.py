from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=v*5!zt6dsf&c_n^3v911de-^3=fjt*1wl+9&xwy8s(r1t0$%u^z#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['content.simfali.ru', '127.0.0.1', 'localhost', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # Добавляем поддержку sitemap
    'media_app'
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

ROOT_URLCONF = 'media_portal.urls'

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
                'media_app.context_processors.categories',  # Обновленный контекстный процессор
                'media_app.context_processors.media_stats',  # Добавляем статистику
            ],
        },
    },
]

WSGI_APPLICATION = 'media_portal.wsgi.application'

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
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Для продакшена
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Создаем директории если их нет
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(BASE_DIR / 'static', exist_ok=True)

# Поддиректории для разных типов медиа
MEDIA_SUBDIRS = {
    'music': MEDIA_ROOT / 'music',
    'music_covers': MEDIA_ROOT / 'music' / 'covers',
    'videos': MEDIA_ROOT / 'videos',
    'video_thumbnails': MEDIA_ROOT / 'videos' / 'thumbnails',
    'photos': MEDIA_ROOT / 'photos',
    'photo_thumbnails': MEDIA_ROOT / 'photos' / 'thumbnails',
    'artists': MEDIA_ROOT / 'artists',
}

# Создаем все поддиректории
for subdir_path in MEDIA_SUBDIRS.values():
    os.makedirs(subdir_path, exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки кэша для оптимизации производительности
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'media-portal-cache',
        'TIMEOUT': 300,  # 5 минут по умолчанию
        'OPTIONS': {
            'MAX_ENTRIES': 2000,  # Увеличиваем для поддержки фотографий
        }
    }
}

# Настройки сессий
SESSION_COOKIE_AGE = 86400  # 24 часа
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Настройки для обработки изображений
THUMBNAIL_SIZE = (300, 300)  # Размер миниатюр по умолчанию
THUMBNAIL_QUALITY = 85  # Качество JPEG для миниатюр
MAX_PHOTO_SIZE = (1920, 1080)  # Максимальный размер для веб-отображения

# Поддерживаемые форматы файлов
SUPPORTED_AUDIO_FORMATS = ['mp3', 'wav', 'ogg', 'flac', 'aac']
SUPPORTED_VIDEO_FORMATS = ['mp4', 'webm', 'ogg', 'avi', 'mov']
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'gif']

# Максимальные размеры файлов (в байтах)
MAX_UPLOAD_SIZE = {
    'audio': 50 * 1024 * 1024,  # 50 MB для аудио
    'video': 500 * 1024 * 1024,  # 500 MB для видео
    'image': 20 * 1024 * 1024,  # 20 MB для изображений
}

# Настройки пагинации
PAGINATION_SETTINGS = {
    'music_per_page': 12,
    'videos_per_page': 9,
    'photos_per_page': 24,
    'albums_per_page': 12,
    'photos_in_album': 20,
}

# Настройки безопасности для продакшена
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'media_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'media_processing.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'media_app': {
            'handlers': ['media_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Создаем директорию для логов
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Настройки для админки
ADMIN_MEDIA_PREFIX = '/admin-media/'

# SEO настройки
DEFAULT_META_DESCRIPTION = "Семейный медиа-портал для хранения музыки, видео и фотографий"
DEFAULT_META_KEYWORDS = "медиа, портал, музыка, видео, фотографии, семейный архив"
SITE_NAME = "Медиа Портал"

# Настройки для разработки
if DEBUG:
    # Дополнительные настройки для отладки
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

    # Отключаем некоторые проверки для ускорения разработки
    CACHES['default']['TIMEOUT'] = 60  # Короткий кэш для разработки

    # Дополнительные приложения для разработки (если установлены)
    try:
        import debug_toolbar

        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
    except ImportError:
        pass

# Конфигурация резервного копирования (для скриптов)
BACKUP_SETTINGS = {
    'database_backup_path': BASE_DIR / 'backups' / 'db',
    'media_backup_path': BASE_DIR / 'backups' / 'media',
    'retention_days': 30,  # Хранить резервные копии 30 дней
}

os.makedirs(BACKUP_SETTINGS['database_backup_path'], exist_ok=True)
os.makedirs(BACKUP_SETTINGS['media_backup_path'], exist_ok=True)
