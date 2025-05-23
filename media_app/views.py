from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch, Count, Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import connection

from .models import Category, Artist, Music, Video

# Главная страница с кэшированием
@cache_page(60 * 15)  # Кэшируем на 15 минут
def home(request):
    # Используем кэш для часто запрашиваемых данных
    latest_music = cache.get('latest_music')
    if not latest_music:
        # Используем select_related для оптимизации запросов к связанным моделям
        latest_music = Music.objects.select_related('artist', 'category').order_by('-created_at')[:5]
        cache.set('latest_music', latest_music, 60 * 15)  # Кэшируем на 15 минут
    
    latest_videos = cache.get('latest_videos')
    if not latest_videos:
        latest_videos = Video.objects.select_related('category').order_by('-created_at')[:5]
        cache.set('latest_videos', latest_videos, 60 * 15)
    
    popular_music = cache.get('popular_music')
    if not popular_music:
        popular_music = Music.objects.select_related('artist', 'category').order_by('-view_count')[:5]
        cache.set('popular_music', popular_music, 60 * 15)
    
    popular_videos = cache.get('popular_videos')
    if not popular_videos:
        popular_videos = Video.objects.select_related('category').order_by('-view_count')[:5]
        cache.set('popular_videos', popular_videos, 60 * 15)
    
    categories = Category.objects.annotate(
        music_count=Count('music_items', distinct=True),
        video_count=Count('video_items', distinct=True)
    ).filter(Q(music_count__gt=0) | Q(video_count__gt=0))
    
    context = {
        'latest_music': latest_music,
        'latest_videos': latest_videos,
        'popular_music': popular_music,
        'popular_videos': popular_videos,
        'categories': categories,
    }
    
    # Для отладки SQL запросов (только в режиме разработки)
    if settings.DEBUG:
        from django.db import connection
        print(f"Количество запросов на главной странице: {len(connection.queries)}")
    
    return render(request, 'media_app/index.html', context)

# Оптимизированный список музыки с кэшированием
@method_decorator(cache_page(60 * 5), name='dispatch')  # Кэширование на 5 минут
class MusicListView(ListView):
    model = Music
    template_name = 'media_app/music_list.html'
    context_object_name = 'music_list'
    paginate_by = 12  # Увеличено количество элементов на странице для уменьшения числа запросов
    
    def get_queryset(self):
        queryset = Music.objects.select_related('artist', 'category')
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Обработка параметров сортировки и поиска
        sort = self.request.GET.get('sort', '')
        query = self.request.GET.get('q', '')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(artist__name__icontains=query) |
                Q(description__icontains=query)
            ).distinct()
        
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'title':
            queryset = queryset.order_by('title')
        elif sort == 'artist':
            queryset = queryset.order_by('artist__name')
        elif sort == 'popular':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Кэшируем категории для боковой панели
        categories = cache.get('categories')
        if not categories:
            categories = Category.objects.annotate(
                music_count=Count('music_items')
            ).filter(music_count__gt=0)
            cache.set('categories', categories, 60 * 30)  # 30 минут
            
        context['categories'] = categories
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
        
        context['sort'] = self.request.GET.get('sort', '')
        context['query'] = self.request.GET.get('q', '')
        
        return context

# Оптимизированный список видео с кэшированием
@method_decorator(cache_page(60 * 5), name='dispatch')  # Кэширование на 5 минут
class VideoListView(ListView):
    model = Video
    template_name = 'media_app/video_list.html'
    context_object_name = 'video_list'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Video.objects.select_related('category')
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Обработка параметров сортировки и поиска
        sort = self.request.GET.get('sort', '')
        query = self.request.GET.get('q', '')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            ).distinct()
        
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'title':
            queryset = queryset.order_by('title')
        elif sort == 'popular':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Кэшируем категории для боковой панели
        video_categories = cache.get('video_categories')
        if not video_categories:
            video_categories = Category.objects.annotate(
                video_count=Count('video_items')
            ).filter(video_count__gt=0)
            cache.set('video_categories', video_categories, 60 * 30)  # 30 минут
            
        context['categories'] = video_categories
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
        
        context['sort'] = self.request.GET.get('sort', '')
        context['query'] = self.request.GET.get('q', '')
        
        return context

# Детальная страница музыки с инкрементным счетчиком просмотров
class MusicDetailView(DetailView):
    model = Music
    template_name = 'media_app/music_detail.html'
    context_object_name = 'music'
    
    def get_queryset(self):
        # Используем select_related для оптимизации запросов
        return Music.objects.select_related('artist', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        music = self.get_object()
        
        # Оптимизированный запрос для похожей музыки
        cache_key = f'related_music_{music.id}'
        related_music = cache.get(cache_key)
        
        if not related_music:
            # Используем тяжелую логику выборки только если нет кэша
            related_music = Music.objects.select_related('artist').filter(
                artist=music.artist
            ).exclude(id=music.id).order_by('-created_at')[:4]
            
            cache.set(cache_key, related_music, 60 * 60)  # Кэшируем на 1 час
        
        context['related_music'] = related_music
        
        # Для удобства добавим также популярные треки этого исполнителя
        popular_artist_tracks = Music.objects.select_related('artist').filter(
            artist=music.artist
        ).exclude(id=music.id).order_by('-view_count')[:4]
        
        context['popular_artist_tracks'] = popular_artist_tracks
        
        return context
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Увеличиваем счетчик просмотров асинхронно
        # Используем ключ сессии, чтобы не учитывать повторные просмотры в течение сеанса
        music = self.object
        session_key = f'viewed_music_{music.id}'
        
        if not request.session.get(session_key, False):
            music.increase_view_count()
            # Устанавливаем флаг сессии на 1 час
            request.session[session_key] = True
            request.session.set_expiry(3600)  # 1 час
        
        return response

# Детальная страница видео с инкрементным счетчиком просмотров
class VideoDetailView(DetailView):
    model = Video
    template_name = 'media_app/video_detail.html'
    context_object_name = 'video'
    
    def get_queryset(self):
        # Используем select_related для оптимизации запросов
        return Video.objects.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        
        # Кэшируем похожие видео
        cache_key = f'related_videos_{video.id}'
        related_videos = cache.get(cache_key)
        
        if not related_videos:
            # Если категория есть, ищем видео в той же категории
            if video.category:
                related_videos = Video.objects.select_related('category').filter(
                    category=video.category
                ).exclude(id=video.id).order_by('-created_at')[:4]
            else:
                # Иначе просто показываем последние видео
                related_videos = Video.objects.select_related('category').exclude(
                    id=video.id
                ).order_by('-created_at')[:4]
            
            cache.set(cache_key, related_videos, 60 * 60)  # Кэшируем на 1 час
        
        context['related_videos'] = related_videos
        
        # Добавляем популярные видео
        popular_videos = Video.objects.select_related('category').exclude(
            id=video.id
        ).order_by('-view_count')[:4]
        
        context['popular_videos'] = popular_videos
        
        return context
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Увеличиваем счетчик просмотров асинхронно
        video = self.object
        session_key = f'viewed_video_{video.id}'
        
        if not request.session.get(session_key, False):
            video.increase_view_count()
            # Устанавливаем флаг сессии на 1 час
            request.session[session_key] = True
            request.session.set_expiry(3600)  # 1 час
        
        return response

# API для получения данных с минимальной нагрузкой
def api_music_info(request, music_id):
    """Легкий API для получения основной информации о треке"""
    try:
        music = Music.objects.get(pk=music_id)
        data = {
            'id': music.id,
            'title': music.title,
            'artist': music.artist.name,
            'audio_url': music.audio_file.url,
            'cover_url': music.cover_image.url if music.cover_image else None,
            'duration': str(music.duration) if music.duration else None,
        }
        return JsonResponse(data)
    except Music.DoesNotExist:
        return JsonResponse({'error': 'Track not found'}, status=404)

def api_video_info(request, video_id):
    """Легкий API для получения основной информации о видео"""
    try:
        video = Video.objects.get(pk=video_id)
        data = {
            'id': video.id,
            'title': video.title,
            'video_url': video.video_file.url,
            'thumbnail_url': video.thumbnail.url if video.thumbnail else None,
            'duration': str(video.duration) if video.duration else None,
        }
        return JsonResponse(data)
    except Video.DoesNotExist:
        return JsonResponse({'error': 'Video not found'}, status=404)

# Контекстный процессор для общей информации на всех страницах
def categories(request):
    """
    Контекстный процессор, который добавляет общие категории во все шаблоны.
    Используется в settings.py в TEMPLATES[0]['OPTIONS']['context_processors']
    """
    # Кэшируем категории для экономии ресурсов
    all_categories = cache.get('all_categories')
    if all_categories is None:
        all_categories = Category.objects.annotate(
            total_items=Count('music_items') + Count('video_items')
        ).filter(total_items__gt=0)
        cache.set('all_categories', all_categories, 60 * 60)  # 1 час
    
    return {
        'all_categories': all_categories
    }