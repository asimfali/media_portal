from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from media_app.sitemaps import (
    StaticViewSitemap, MusicSitemap, VideoSitemap,
    AlbumSitemap, PhotoSitemap, CategorySitemap
)

sitemaps = {
    'static': StaticViewSitemap,
    'music': MusicSitemap,
    'videos': VideoSitemap,
    'albums': AlbumSitemap,
    'photos': PhotoSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('media_app.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Добавляем URL-паттерны для обработки медиа-файлов (только в режиме разработки)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
