import os
import shutil
import datetime
from pathlib import Path
import sqlite3
import zipfile


def backup_database(source_db, backup_dir):
    """Создает резервную копию базы данных SQLite"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'db_backup_{timestamp}.sqlite3'
    backup_path = backup_dir / backup_filename

    # Копируем базу данных
    shutil.copy2(source_db, backup_path)

    # Создаем ZIP архив
    zip_path = backup_dir / f'db_backup_{timestamp}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(backup_path, backup_filename)

    # Удаляем временный файл
    os.remove(backup_path)

    return zip_path


def backup_media(media_dir, backup_dir):
    """Создает резервную копию медиа файлов"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'media_backup_{timestamp}'

    # Создаем tar.gz архив
    shutil.make_archive(
        backup_dir / backup_filename,
        'gztar',
        media_dir
    )

    return backup_dir / f'{backup_filename}.tar.gz'


def cleanup_old_backups(backup_dir, retention_days=30):
    """Удаляет старые резервные копии"""
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)

    for backup_file in backup_dir.glob('*'):
        if backup_file.is_file():
            file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_date:
                backup_file.unlink()
                print(f"Удален старый бэкап: {backup_file}")


def main():
    """Основная функция создания резервных копий"""
    from django.conf import settings

    print("Начинаем создание резервных копий...")

    # Резервная копия базы данных
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        db_backup = backup_database(
            settings.DATABASES['default']['NAME'],
            settings.BACKUP_SETTINGS['database_backup_path']
        )
        print(f"База данных скопирована: {db_backup}")

    # Резервная копия медиа файлов
    media_backup = backup_media(
        settings.MEDIA_ROOT,
        settings.BACKUP_SETTINGS['media_backup_path']
    )
    print(f"Медиа файлы скопированы: {media_backup}")

    # Очистка старых резервных копий
    cleanup_old_backups(
        settings.BACKUP_SETTINGS['database_backup_path'],
        settings.BACKUP_SETTINGS['retention_days']
    )
    cleanup_old_backups(
        settings.BACKUP_SETTINGS['media_backup_path'],
        settings.BACKUP_SETTINGS['retention_days']
    )

    print("Резервное копирование завершено!")


if __name__ == '__main__':
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'media_portal.settings')
    django.setup()
    main()