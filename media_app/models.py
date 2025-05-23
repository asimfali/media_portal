from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import os
from mutagen.mp3 import MP3
from datetime import timedelta
import uuid

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
            models.Index(fields=['view_count']),    # Индекс для счетчика просмотров
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
            models.Index(fields=['view_count']),   # Индекс для счетчика просмотров
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