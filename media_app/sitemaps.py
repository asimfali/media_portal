from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Music, Video, Album, Photo, Category


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'music_list', 'video_list', 'album_list', 'photo_list']

    def location(self, item):
        return reverse(item)


class MusicSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Music.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class VideoSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Video.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class AlbumSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Album.objects.filter(is_private=False)

    def lastmod(self, obj):
        return obj.updated_at


class PhotoSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Photo.objects.filter(album__is_private=False)

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Category.objects.all()
