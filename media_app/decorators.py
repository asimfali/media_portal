from functools import wraps
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Album


def require_public_album(view_func):
    """
    Декоратор для проверки, что альбом не приватный
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'slug' in kwargs:
            album = get_object_or_404(Album, slug=kwargs['slug'])
            if album.is_private:
                raise Http404("Альбом не найден")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_public_photo(view_func):
    """
    Декоратор для проверки, что фотография из публичного альбома
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'pk' in kwargs:
            from .models import Photo
            photo = get_object_or_404(Photo, pk=kwargs['pk'])
            if photo.album.is_private:
                raise Http404("Фотография не найдена")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
