from django import forms
from .models import Photo, Album, Music, Video, Category


class PhotoAdminForm(forms.ModelForm):
    """Форма для редактирования фотографий в админке"""

    class Meta:
        model = Photo
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Введите теги через запятую'}),
            'location_name': forms.TextInput(attrs={'placeholder': 'Название места'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем альбомы только не приватные для обычных пользователей
        if not self.instance.pk:
            self.fields['album'].queryset = Album.objects.filter(is_private=False)


class AlbumAdminForm(forms.ModelForm):
    """Форма для редактирования альбомов в админке"""

    class Meta:
        model = Album
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class BulkUploadForm(forms.Form):
    """Форма для массовой загрузки фотографий"""
    album = forms.ModelChoiceField(
        queryset=Album.objects.all(),
        label="Альбом",
        help_text="Выберите альбом для загрузки фотографий"
    )
    photos = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label="Фотографии",
        help_text="Выберите несколько фотографий для загрузки"
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория",
        help_text="Необязательно: категория для всех загружаемых фотографий"
    )