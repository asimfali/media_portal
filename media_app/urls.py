from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Музыка
    path('music/', views.MusicListView.as_view(), name='music_list'),
    path('music/category/<slug:category_slug>/', views.MusicListView.as_view(), name='music_by_category'),
    path('music/<int:pk>/', views.MusicDetailView.as_view(), name='music_detail'),

    # Видео
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('videos/category/<slug:category_slug>/', views.VideoListView.as_view(), name='video_by_category'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),

    # API endpoints
    path('api/music/<int:music_id>/', views.api_music_info, name='api_music_info'),
    path('api/video/<int:video_id>/', views.api_video_info, name='api_video_info'),

    path('albums/', views.AlbumListView.as_view(), name='album_list'),
    path('albums/category/<slug:category_slug>/', views.AlbumListView.as_view(), name='albums_by_category'),
    path('album/<slug:slug>/', views.AlbumDetailView.as_view(), name='album_detail'),

    # Фотографии
    path('photos/', views.PhotoListView.as_view(), name='photo_list'),
    path('photos/category/<slug:category_slug>/', views.PhotoListView.as_view(), name='photos_by_category'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),

    # API для фотографий
    path('api/photo/<int:photo_id>/', views.api_photo_info, name='api_photo_info'),
]