from PIL import Image, ExifTags
from django.core.files.base import ContentFile
from io import BytesIO
import os
import hashlib
from django.conf import settings


def create_photo_thumbnail(image_path, size=(300, 300), quality=85):
    """
    Создает миниатюру изображения
    """
    try:
        with Image.open(image_path) as img:
            # Сохраняем ориентацию
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        decoded = ExifTags.TAGS.get(tag, tag)
                        if decoded == 'Orientation':
                            if value == 3:
                                img = img.rotate(180, expand=True)
                            elif value == 6:
                                img = img.rotate(270, expand=True)
                            elif value == 8:
                                img = img.rotate(90, expand=True)

            # Создаем миниатюру
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Сохраняем в буфер
            output = BytesIO()
            format = img.format if img.format else 'JPEG'
            img.save(output, format=format, quality=quality, optimize=True)
            output.seek(0)

            return output.getvalue()

    except Exception as e:
        print(f"Ошибка создания миниатюры: {e}")
        return None


def extract_photo_metadata(image_path):
    """
    Извлекает метаданные из фотографии
    """
    metadata = {
        'width': 0,
        'height': 0,
        'taken_at': None,
        'camera_model': '',
        'camera_settings': {},
        'gps_data': None
    }

    try:
        with Image.open(image_path) as img:
            # Размеры
            metadata['width'], metadata['height'] = img.size

            # EXIF данные
            exif = img.getexif()
            if exif:
                # Дата съемки
                for key in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                    if key in exif:
                        try:
                            from datetime import datetime
                            metadata['taken_at'] = datetime.strptime(
                                str(exif[key]), '%Y:%m:%d %H:%M:%S'
                            )
                            break
                        except:
                            pass

                # Модель камеры
                if 'Make' in exif and 'Model' in exif:
                    metadata['camera_model'] = f"{exif['Make']} {exif['Model']}".strip()
                elif 'Model' in exif:
                    metadata['camera_model'] = str(exif['Model'])

                # Настройки камеры
                camera_settings = {}
                settings_map = {
                    'FNumber': 'Диафрагма',
                    'ExposureTime': 'Выдержка',
                    'ISOSpeedRatings': 'ISO',
                    'FocalLength': 'Фокусное расстояние',
                    'Flash': 'Вспышка'
                }

                for exif_key, readable_key in settings_map.items():
                    if exif_key in exif:
                        camera_settings[readable_key] = str(exif[exif_key])

                if camera_settings:
                    metadata['camera_settings'] = camera_settings

                # GPS данные
                if 'GPSInfo' in exif:
                    gps_info = exif['GPSInfo']
                    if gps_info:
                        metadata['gps_data'] = dict(gps_info)

    except Exception as e:
        print(f"Ошибка извлечения метаданных: {e}")

    return metadata


def calculate_file_hash(file_path):
    """
    Вычисляет хеш файла для обнаружения дубликатов
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None


def optimize_image_for_web(image_path, max_width=1920, max_height=1080, quality=85):
    """
    Оптимизирует изображение для веб-использования
    """
    try:
        with Image.open(image_path) as img:
            # Конвертируем в RGB если необходимо
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Изменяем размер если изображение слишком большое
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Сохраняем оптимизированную версию
            optimized_path = image_path.replace('.', '_optimized.')
            img.save(optimized_path, 'JPEG', quality=quality, optimize=True)

            return optimized_path

    except Exception as e:
        print(f"Ошибка оптимизации изображения: {e}")
        return image_path
