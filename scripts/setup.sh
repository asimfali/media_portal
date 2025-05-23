# scripts/setup.sh - Скрипт первоначальной настройки
#!/bin/bash

echo "Настройка Медиа Портала..."

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание необходимых директорий
mkdir -p media/{music,videos,photos,artists}
mkdir -p media/music/covers
mkdir -p media/videos/thumbnails
mkdir -p media/photos/thumbnails
mkdir -p static
mkdir -p logs
mkdir -p backups/{db,media}

# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
echo "Создание администратора:"
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic --noinput

echo "Настройка завершена! Запустите: python manage.py runserver"