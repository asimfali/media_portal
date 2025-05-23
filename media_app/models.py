from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import os
from mutagen.mp3 import MP3
from datetime import timedelta
import uuid
from PIL import Image as PILImage
from django.core.files.base import ContentFile
from io import BytesIO


class Category(models.Model):
    """Модель для категорий медиа-контента"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),  # Добавляем индекс для slug
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автоматически создаем slug при создании категории
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Artist(models.Model):
    """Модель для исполнителей музыки"""
    name = models.CharField(max_length=200, verbose_name="Имя исполнителя")
    bio = models.TextField(blank=True, verbose_name="Биография")
    image = models.ImageField(
        upload_to='artists/',
        blank=True,
        verbose_name="Фото исполнителя",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),  # Индекс для имени исполнителя
        ]

    def __str__(self):
        return self.name


def music_file_path(instance, filename):
    """Генерация уникального пути для музыкальных файлов"""
    # Получаем расширение оригинального файла
    ext = filename.split('.')[-1]
    # Создаем имя файла на основе имени исполнителя, названия трека и случайного UUID
    filename = f"{slugify(instance.artist.name)}-{slugify(instance.title)}-{uuid.uuid4().hex}.{ext}"
    return os.path.join('music', filename)


def cover_image_path(instance, filename):
    """Генерация уникального пути для обложек треков"""
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.artist.name)}-{slugify(instance.title)}-cover-{uuid.uuid4().hex}.{ext}"
    return os.path.join('music/covers', filename)


class Music(models.Model):
    """Модель для музыкальных треков с оптимизацией"""
    title = models.CharField(max_length=200, verbose_name="Название трека")
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="tracks",
        verbose_name="Исполнитель",
        db_index=True  # Добавляем индекс для внешнего ключа
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="music_items",
        verbose_name="Категория",
        db_index=True  # Добавляем индекс
    )
    audio_file = models.FileField(
        upload_to=music_file_path,
        verbose_name="Аудио файл",
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg'])]
    )
    cover_image = models.ImageField(
        upload_to=cover_image_path,
        blank=True,
        verbose_name="Обложка",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    duration = models.DurationField(null=True, blank=True, verbose_name="Продолжительность")
    release_date = models.DateField(verbose_name="Дата выпуска")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    file_size = models.PositiveIntegerField(default=0, verbose_name="Размер файла (байты)")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Количество прослушиваний")

    class Meta:
        verbose_name = "Музыкальный трек"
        verbose_name_plural = "Музыкальные треки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),  # Индекс для сортировки по дате
            models.Index(fields=['release_date']),  # Индекс для даты выпуска
            models.Index(fields=['view_count']),  # Индекс для счетчика просмотров
        ]

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def get_absolute_url(self):
        return reverse('music_detail', args=[str(self.id)])

    def increase_view_count(self):
        """Увеличение счетчика просмотров с оптимизацией"""
        # Используем F() для атомарного обновления счетчика без гонки данных
        from django.db.models import F
        self.view_count = F('view_count') + 1
        self.save(update_fields=['view_count'])


def video_file_path(instance, filename):
    """Генерация уникального пути для видео файлов"""
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}-{uuid.uuid4().hex}.{ext}"
    return os.path.join('videos', filename)


def thumbnail_path(instance, filename):
    """Генерация уникального пути для превью видео"""
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}-thumb-{uuid.uuid4().hex}.{ext}"
    return os.path.join('videos/thumbnails', filename)


class Video(models.Model):
    """Модель для видео с оптимизацией"""
    title = models.CharField(max_length=200, verbose_name="Название видео")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_items",
        verbose_name="Категория",
        db_index=True  # Индекс для внешнего ключа
    )
    video_file = models.FileField(
        upload_to=video_file_path,
        verbose_name="Видео файл",
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])]
    )
    thumbnail = models.ImageField(
        upload_to=thumbnail_path,
        blank=True,
        verbose_name="Превью",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    duration = models.DurationField(null=True, blank=True, verbose_name="Продолжительность")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    file_size = models.PositiveIntegerField(default=0, verbose_name="Размер файла (байты)")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")

    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),  # Индекс для сортировки по дате
            models.Index(fields=['view_count']),  # Индекс для счетчика просмотров
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('video_detail', args=[str(self.id)])

    def increase_view_count(self):
        """Увеличение счетчика просмотров с оптимизацией"""
        from django.db.models import F
        self.view_count = F('view_count') + 1
        self.save(update_fields=['view_count'])


# Сигналы для автоматического вычисления продолжительности и размера файла
@receiver(post_save, sender=Music)
def set_music_duration(sender, instance, created, **kwargs):
    """Автоматически вычисляет продолжительность MP3 после сохранения"""
    if instance.audio_file and not instance.duration:
        try:
            audio = MP3(instance.audio_file.path)
            duration = timedelta(seconds=int(audio.info.length))

            # Получаем размер файла
            file_size = os.path.getsize(instance.audio_file.path)

            # Используем update() для избежания рекурсивного вызова сигнала
            Music.objects.filter(pk=instance.pk).update(
                duration=duration,
                file_size=file_size
            )
        except Exception as e:
            # Логируем ошибку, но не блокируем сохранение
            print(f"Ошибка при определении длительности аудио: {e}")


@receiver(post_save, sender=Video)
def set_video_file_size(sender, instance, created, **kwargs):
    """Автоматически вычисляет размер видео-файла после сохранения"""
    if instance.video_file and instance.file_size == 0:
        try:
            # Получаем размер файла
            file_size = os.path.getsize(instance.video_file.path)

            # Используем update() для избежания рекурсивного вызова сигнала
            Video.objects.filter(pk=instance.pk).update(file_size=file_size)
        except Exception as e:
            print(f"Ошибка при определении размера видео: {e}")


def photo_file_path(instance, filename):
    """Генерация уникального пути для фотографий"""
    ext = filename.split('.')[-1].lower()
    filename = f"{slugify(instance.title)}-{uuid.uuid4().hex}.{ext}"
    return os.path.join('photos', filename)


def photo_thumbnail_path(instance, filename):
    """Генерация пути для миниатюр фотографий"""
    ext = filename.split('.')[-1].lower()
    filename = f"{slugify(instance.title)}-thumb-{uuid.uuid4().hex}.{ext}"
    return os.path.join('photos/thumbnails', filename)


class Album(models.Model):
    """Модель для альбомов фотографий"""
    title = models.CharField(max_length=200, verbose_name="Название альбома")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL альбома")
    description = models.TextField(blank=True, verbose_name="Описание альбома")
    cover_photo = models.ForeignKey(
        'Photo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_for_albums',
        verbose_name="Обложка альбома"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="album_items",
        verbose_name="Категория",
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_private = models.BooleanField(default=False, verbose_name="Приватный альбом")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    photo_count = models.PositiveIntegerField(default=0, verbose_name="Количество фотографий")

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['is_private']),
            models.Index(fields=['view_count']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('album_detail', args=[str(self.slug)])

    def increase_view_count(self):
        """Увеличение счетчика просмотров альбома"""
        from django.db.models import F
        self.view_count = F('view_count') + 1
        self.save(update_fields=['view_count'])

    def update_photo_count(self):
        """Обновление счетчика фотографий в альбоме"""
        self.photo_count = self.photos.count()
        self.save(update_fields=['photo_count'])


class Photo(models.Model):
    """Модель для фотографий с оптимизацией"""
    title = models.CharField(max_length=200, verbose_name="Название фотографии")
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Альбом",
        db_index=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="photo_items",
        verbose_name="Категория",
        db_index=True
    )
    image = models.ImageField(
        upload_to=photo_file_path,
        verbose_name="Изображение",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp'])]
    )
    thumbnail = models.ImageField(
        upload_to=photo_thumbnail_path,
        blank=True,
        verbose_name="Миниатюра"
    )
    description = models.TextField(blank=True, verbose_name="Описание")

    # EXIF данные
    taken_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата съемки")
    camera_model = models.CharField(max_length=100, blank=True, verbose_name="Модель камеры")
    camera_settings = models.JSONField(default=dict, blank=True, verbose_name="Настройки камеры")

    # Геолокация
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    location_name = models.CharField(max_length=200, blank=True, verbose_name="Название места")

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    file_size = models.PositiveIntegerField(default=0, verbose_name="Размер файла (байты)")
    width = models.PositiveIntegerField(default=0, verbose_name="Ширина изображения")
    height = models.PositiveIntegerField(default=0, verbose_name="Высота изображения")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")

    # Теги для поиска
    tags = models.CharField(max_length=500, blank=True, verbose_name="Теги (через запятую)")

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['taken_at']),
            models.Index(fields=['view_count']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.title} ({self.album.title})"

    def get_absolute_url(self):
        return reverse('photo_detail', args=[str(self.id)])

    def increase_view_count(self):
        """Увеличение счетчика просмотров фотографии"""
        from django.db.models import F
        self.view_count = F('view_count') + 1
        self.save(update_fields=['view_count'])

    def create_thumbnail(self):
        """Создание миниатюры изображения"""
        if not self.image:
            return

        try:
            with PILImage.open(self.image.path) as img:
                # Создаем миниатюру размером 300x300 пикселей
                img.thumbnail((300, 300), PILImage.Resampling.LANCZOS)

                # Сохраняем в буфер
                output = BytesIO()
                format = img.format if img.format else 'JPEG'
                img.save(output, format=format, quality=85, optimize=True)
                output.seek(0)

                # Создаем имя файла для миниатюры
                name = f"{self.title}-thumb.{format.lower()}"
                self.thumbnail.save(name, ContentFile(output.read()), save=False)

        except Exception as e:
            print(f"Ошибка создания миниатюры для {self.title}: {e}")

    def extract_exif_data(self):
        """Извлечение EXIF данных из изображения"""
        if not self.image:
            return

        try:
            from PIL import Image as PILImage
            from PIL.ExifTags import TAGS
            import datetime

            with PILImage.open(self.image.path) as img:
                # Получаем размеры изображения
                self.width, self.height = img.size

                # Получаем EXIF данные
                exifdata = img.getexif()
                if exifdata:
                    exif_dict = {}
                    for tag_id in exifdata:
                        tag = TAGS.get(tag_id, tag_id)
                        data = exifdata.get(tag_id)
                        exif_dict[tag] = data

                    # Извлекаем дату съемки
                    if 'DateTime' in exif_dict:
                        try:
                            self.taken_at = datetime.datetime.strptime(
                                exif_dict['DateTime'], '%Y:%m:%d %H:%M:%S'
                            )
                        except ValueError:
                            pass

                    # Извлекаем модель камеры
                    if 'Model' in exif_dict:
                        self.camera_model = str(exif_dict['Model'])

                    # Сохраняем настройки камеры
                    camera_settings = {}
                    for key in ['FNumber', 'ExposureTime', 'ISOSpeedRatings', 'FocalLength']:
                        if key in exif_dict:
                            camera_settings[key] = str(exif_dict[key])

                    if camera_settings:
                        self.camera_settings = camera_settings

                    # Извлекаем GPS координаты
                    if 'GPSInfo' in exif_dict:
                        gps_info = exif_dict['GPSInfo']
                        if gps_info:
                            # Здесь можно добавить более сложную логику извлечения GPS
                            pass

        except Exception as e:
            print(f"Ошибка извлечения EXIF для {self.title}: {e}")


# Сигналы для автоматической обработки изображений
@receiver(post_save, sender=Photo)
def process_photo(sender, instance, created, **kwargs):
    """Автоматическая обработка фотографии после сохранения"""
    if created and instance.image:
        try:
            # Извлекаем EXIF данные
            instance.extract_exif_data()

            # Получаем размер файла
            instance.file_size = os.path.getsize(instance.image.path)

            # Создаем миниатюру
            instance.create_thumbnail()

            # Обновляем запись без вызова сигнала
            Photo.objects.filter(pk=instance.pk).update(
                width=instance.width,
                height=instance.height,
                file_size=instance.file_size,
                taken_at=instance.taken_at,
                camera_model=instance.camera_model,
                camera_settings=instance.camera_settings
            )

            # Обновляем счетчик фотографий в альбоме
            instance.album.update_photo_count()

        except Exception as e:
            print(f"Ошибка обработки фотографии {instance.title}: {e}")


@receiver(post_delete, sender=Photo)
def update_album_count_on_delete(sender, instance, **kwargs):
    """Обновление счетчика фотографий при удалении"""
    if instance.album:
        instance.album.update_photo_count()
