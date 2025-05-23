from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Разделяет строку на список по разделителю"""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]


@register.filter
def filesizeformat_short(bytes):
    """Короткий формат размера файла"""
    try:
        bytes = float(bytes)
    except (TypeError, ValueError, UnicodeDecodeError):
        return "0 B"

    if bytes < 1024:
        return f"{bytes:.0f} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.1f} GB"


@register.filter
def duration_format(duration):
    """Форматирует продолжительность в читаемый вид"""
    if not duration:
        return ""

    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


@register.filter
def split(value, delimiter=','):
    """Разделяет строку на список по разделителю"""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]


@register.simple_tag
def photo_grid_class(photo_count):
    """Возвращает CSS-класс для сетки фотографий в зависимости от количества"""
    if photo_count == 1:
        return "grid-cols-1"
    elif photo_count == 2:
        return "grid-cols-2"
    elif photo_count <= 4:
        return "grid-cols-2 lg:grid-cols-2"
    elif photo_count <= 6:
        return "grid-cols-2 sm:grid-cols-3"
    else:
        return "grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5"


@register.inclusion_tag('media_app/components/breadcrumbs.html')
def breadcrumbs(current_page, category=None):
    """Генерирует хлебные крошки для навигации"""
    crumbs = [{'title': 'Главная', 'url': '/'}]

    if current_page == 'music_list':
        crumbs.append({'title': 'Музыка', 'url': None})
    elif current_page == 'video_list':
        crumbs.append({'title': 'Видео', 'url': None})
    elif current_page == 'album_list':
        crumbs.append({'title': 'Фотоальбомы', 'url': None})
    elif current_page == 'photo_list':
        crumbs.append({'title': 'Фотографии', 'url': None})

    if category:
        if current_page in ['music_list', 'music_by_category']:
            crumbs[-1]['url'] = '/music/'
        elif current_page in ['video_list', 'video_by_category']:
            crumbs[-1]['url'] = '/videos/'
        elif current_page in ['album_list', 'albums_by_category']:
            crumbs[-1]['url'] = '/albums/'
        elif current_page in ['photo_list', 'photos_by_category']:
            crumbs[-1]['url'] = '/photos/'

        crumbs.append({'title': category.name, 'url': None})

    return {'crumbs': crumbs}
