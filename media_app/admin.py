from django.contrib import admin
from .models import Category, Artist, Music, Video, Photo, Album


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'category', 'release_date', 'created_at']
    list_filter = ['artist', 'category', 'release_date']
    search_fields = ['title', 'artist__name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'artist', 'category', 'description')
        }),
        ('Медиа файлы', {
            'fields': ('audio_file', 'cover_image')
        }),
        ('Метаданные', {
            'fields': ('duration', 'release_date', 'created_at')
        }),
    )

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'category', 'description')
        }),
        ('Медиа файлы', {
            'fields': ('video_file', 'thumbnail')
        }),
        ('Метаданные', {
            'fields': ('duration', 'created_at')
        }),
    )


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'photo_count', 'view_count', 'is_private', 'created_at']
    list_filter = ['category', 'is_private', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'photo_count']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Настройки', {
            'fields': ('cover_photo', 'is_private')
        }),
        ('Статистика', {
            'fields': ('photo_count', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'category', 'taken_at', 'view_count', 'created_at']
    list_filter = ['album', 'category', 'taken_at', 'created_at']
    search_fields = ['title', 'description', 'tags', 'album__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'width', 'height', 'file_size', 'camera_model', 'camera_settings']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'album', 'category', 'description', 'tags')
        }),
        ('Медиа файлы', {
            'fields': ('image', 'thumbnail')
        }),
        ('Метаданные изображения', {
            'fields': ('width', 'height', 'file_size', 'taken_at', 'camera_model', 'camera_settings'),
            'classes': ('collapse',)
        }),
        ('Геолокация', {
            'fields': ('location_name', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('view_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('album', 'category')