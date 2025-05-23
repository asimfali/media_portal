from django.contrib import admin
from .models import Category, Artist, Music, Video

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