from django.core.management.base import BaseCommand
from media_app.models import Photo
from PIL import Image
import os


class Command(BaseCommand):
    help = 'Генерирует миниатюры для всех фотографий'

    def add_arguments(self, parser):
        parser.add_argument(
            '--size',
            type=int,
            default=300,
            help='Размер миниатюры (по умолчанию 300px)',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='Качество JPEG (по умолчанию 85)',
        )

    def handle(self, *args, **options):
        size = options['size']
        quality = options['quality']

        photos = Photo.objects.filter(thumbnail='')
        total = photos.count()

        self.stdout.write(f'Генерация миниатюр размером {size}x{size} для {total} фотографий...')

        success_count = 0
        error_count = 0

        for i, photo in enumerate(photos, 1):
            try:
                if photo.image and os.path.exists(photo.image.path):
                    # Создаем миниатюру
                    with Image.open(photo.image.path) as img:
                        img.thumbnail((size, size), Image.Resampling.LANCZOS)

                        # Определяем формат
                        format = img.format if img.format else 'JPEG'

                        # Создаем путь для миниатюры
                        thumb_path = photo.image.path.replace(
                            os.path.splitext(photo.image.path)[1],
                            f'_thumb{os.path.splitext(photo.image.path)[1]}'
                        )

                        # Сохраняем миниатюру
                        img.save(thumb_path, format=format, quality=quality, optimize=True)

                        # Обновляем поле thumbnail
                        photo.thumbnail.name = thumb_path.replace(photo.image.storage.location, '').lstrip('/')
                        photo.save(update_fields=['thumbnail'])

                        success_count += 1

                        if i % 10 == 0:
                            self.stdout.write(f'Обработано {i}/{total}...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка обработки {photo.title}: {str(e)}')
                )
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово! Успешно: {success_count}, Ошибок: {error_count}'
            )
        )