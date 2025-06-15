# news/forms.py
from django import forms
from .models import News, NewsImage
from django.forms.models import inlineformset_factory

from django import forms
from django.forms.models import inlineformset_factory
from .models import News, NewsImage

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'category', 'summary', 'body', 'main_image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # گرفتن کاربر از ویو
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = user.allowed_categories.all()


NewsImageFormSet = inlineformset_factory(
    News, NewsImage,
    fields=['image'],
    extra=1,
    can_delete=True
)




# news/forms.py
from django import forms
from .models import Category




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']  # slug اضافه شده
        labels = {
            'name': 'نام دسته‌بندی',
            'slug': 'نامک (slug)',
        }
