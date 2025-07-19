# news/forms.py
from django import forms
from .models import News, NewsImage
from django.forms.models import inlineformset_factory

from django import forms
from django.forms.models import inlineformset_factory
from .models import News, NewsImage




from django import forms
from django.forms import inlineformset_factory
from .models import News, NewsImage, NewsLink

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'category', 'summary', 'body', 'main_image']
        widgets = {
            'category': forms.Select(attrs={'id': 'id_category'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = user.allowed_categories.all()


# 📷 فرم ست تصاویر اضافه‌ای خبر
NewsImageFormSet = inlineformset_factory(
    News, NewsImage,
    fields=['image'],
    extra=1,
    can_delete=True
)

# 🔗 فرم ست لینک‌های اضافه‌شده به خبر
NewsLinkFormSet = inlineformset_factory(
    News, NewsLink,
    fields=['title', 'url'],
    extra=1,
    can_delete=True
)








# news/forms.py
from django import forms
from .models import Category





# news/forms.py

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'daily_limit']
        labels = {
            'name': 'نام دسته‌بندی',
            'slug': 'نامک (slug)',
            'daily_limit': 'سقف ارسال روزانه',
        }
        help_texts = {
            'daily_limit': 'اگر صفر باشد محدودیتی ندارد.',
        }






from django import forms
from .models import Comment
from accounts.models import Persona


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['persona', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'نظر خود را بنویسید...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            personas = user.personas.all()
            self.fields['persona'].queryset = personas

            # انتخاب پیش‌فرض بر اساس نوع شخصیت
            legal_persona = personas.filter(persona_type='legal').first()
            real_persona = personas.filter(persona_type='real').first()

            if not self.instance.pk:  # فقط برای ایجاد، نه ویرایش
                if legal_persona:
                    self.initial['persona'] = legal_persona
                elif real_persona:
                    self.initial['persona'] = real_persona
