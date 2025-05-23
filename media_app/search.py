from django.db.models import Q
from django.core.paginator import Paginator
from .models import Music, Video, Photo, Album


def search_all_media(query, page=1, per_page=20):
    """
    Универсальный поиск по всем типам медиа
    """
    results = {
        'music': [],
        'videos': [],
        'photos': [],
        'albums': [],
        'total_count': 0
    }

    if not query:
        return results

    # Поиск музыки
    music_results = Music.objects.select_related('artist', 'category').filter(
        Q(title__icontains=query) |
        Q(artist__name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()

    # Поиск видео
    video_results = Video.objects.select_related('category').filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()

    # Поиск фотографий
    photo_results = Photo.objects.select_related('album', 'category').filter(
        album__is_private=False
    ).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query) |
        Q(album__title__icontains=query) |
        Q(category__name__icontains=query) |
        Q(location_name__icontains=query)
    ).distinct()

    # Поиск альбомов
    album_results = Album.objects.select_related('category').filter(
        is_private=False
    ).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()

    results['music'] = music_results[:5]  # Показываем первые 5 результатов каждого типа
    results['videos'] = video_results[:5]
    results['photos'] = photo_results[:5]
    results['albums'] = album_results[:5]
    results['total_count'] = (
            music_results.count() +
            video_results.count() +
            photo_results.count() +
            album_results.count()
    )

    return results