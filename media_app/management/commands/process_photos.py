from django.core.management.base import BaseCommand
from media_app.models import Photo
from PIL import Image
import os


class Command(BaseCommand):
    help = 'Обрабатывает все фотографии: создает миниатюры и извлекает EXIF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Переобработать все фотографии, включая уже обработанные',
        )

    def handle(self, *args, **options):
        force = options['force']

        if force:
            photos = Photo.objects.all()
            self.stdout.write('Переобработка всех фотографий...')
        else:
            photos = Photo.objects.filter(thumbnail='')
            self.stdout.write('Обработка фотографий без миниатюр...')

        total_photos = photos.count()
        processed = 0
        errors = 0

        for photo in photos:
            try:
                self.stdout.write(f'Обработка: {photo.title}')

                # Извлекаем EXIF данные
                photo.extract_exif_data()

                # Создаем миниатюру если её нет или принудительная обработка
                if not photo.thumbnail or force:
                    photo.create_thumbnail()

                # Обновляем размер файла
                if photo.image and os.path.exists(photo.image.path):
                    photo.file_size = os.path.getsize(photo.image.path)

                photo.save()
                processed += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка обработки фото {photo.id}: {str(e)}')
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Обработано: {processed} из {total_photos}. Ошибок: {errors}'
            )
        )
