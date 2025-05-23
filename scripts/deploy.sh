#!/bin/bash

echo "Начинаем развертывание Медиа Портала..."

# Остановка сервиса (если запущен)
sudo systemctl stop media-portal || true

# Обновление кода
git pull origin main

# Активация виртуального окружения
source venv/bin/activate

# Установка/обновление зависимостей
pip install -r requirements.txt

# Миграции базы данных
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic --noinput

# Обработка медиа файлов
python manage.py process_photos

# Создание резервной копии
python scripts/backup.py

# Перезапуск сервиса
sudo systemctl start media-portal
sudo systemctl enable media-portal

echo "Развертывание завершено!"
