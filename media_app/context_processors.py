from django.core.cache import cache
from django.db.models import Count, Q
from .models import Category, Music, Video, Photo, Album


def media_stats(request):
    """
    Контекстный процессор для общей статистики медиа-портала
    """
    stats = cache.get('media_portal_stats')
    if not stats:
        stats = {
            'total_music_tracks': Music.objects.count(),
            'total_videos': Video.objects.count(),
            'total_photos': Photo.objects.filter(album__is_private=False).count(),
            'total_albums': Album.objects.filter(is_private=False).count(),
            'total_categories': Category.objects.count(),
        }
        cache.set('media_portal_stats', stats, 60 * 60)  # Кэш на час

    return {'media_stats': stats}


def categories(request):
    """
    Обновленный контекстный процессор для категорий с фотографиями
    """
    all_categories = cache.get('all_categories_with_photos')
    if all_categories is None:
        all_categories = Category.objects.annotate(
            music_count=Count('music_items', distinct=True),
            video_count=Count('video_items', distinct=True),
            photo_count=Count('photo_items', distinct=True),
            album_count=Count('album_items', distinct=True),
            total_items=Count('music_items', distinct=True) +
                        Count('video_items', distinct=True) +
                        Count('photo_items', distinct=True) +
                        Count('album_items', distinct=True)
        ).filter(total_items__gt=0).order_by('name')
        cache.set('all_categories_with_photos', all_categories, 60 * 60)  # 1 час

    return {
        'all_categories': all_categories
    }