from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
import jdatetime
from django import forms
from .models import Martyr, MartyrMemory

import jdatetime
from django import forms
from .models import Martyr

import jdatetime
from django import forms
from .models import Martyr

class MartyrForm(forms.ModelForm):
    birth_date = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'birth_date_picker',
            'autocomplete': 'off',
            'placeholder': 'تاریخ تولد',
        })
    )
    martyr_date = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'martyr_date_picker',
            'autocomplete': 'off',
            'placeholder': 'تاریخ شهادت',
        })
    )

    class Meta:
        model = Martyr
        exclude = ['birth_date', 'martyr_date']  # ❗️اینجا اصلاح شد

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            if self.instance and self.instance.birth_date:
                try:
                    self.fields['birth_date'].initial = jdatetime.date.fromgregorian(date=self.instance.birth_date).strftime('%Y/%m/%d')
                except:
                    pass
            if self.instance and self.instance.martyr_date:
                try:
                    self.fields['martyr_date'].initial = jdatetime.date.fromgregorian(date=self.instance.martyr_date).strftime('%Y/%m/%d')
                except:
                    pass

    def clean_birth_date(self):
        date_str = self.cleaned_data.get('birth_date')
        if date_str:
            try:
                y, m, d = map(int, date_str.replace('-', '/').split('/'))
                return jdatetime.date(y, m, d).togregorian()
            except:
                raise forms.ValidationError("تاریخ تولد نامعتبر است.")
        return None

    def clean_martyr_date(self):
        date_str = self.cleaned_data.get('martyr_date')
        if date_str:
            try:
                y, m, d = map(int, date_str.replace('-', '/').split('/'))
                return jdatetime.date(y, m, d).togregorian()
            except:
                raise forms.ValidationError("تاریخ شهادت نامعتبر است.")
        return None




from django import forms
from .models import MartyrMemory
from accounts.models import Persona

class MartyrMemoryForm(forms.ModelForm):
    class Meta:
        model = MartyrMemory
        fields = ['persona', 'text', 'image', 'audio']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            queryset = Persona.objects.filter(user=user)
            self.fields['persona'].queryset = queryset

            # 🔹 پیش‌فرض انتخاب حقیقی
            real_persona = queryset.filter(persona_type='real').first()
            if real_persona:
                self.fields['persona'].initial = real_persona.pk



class MartyrUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Martyr
    form_class = MartyrForm
    template_name = 'martyrs/martyr_edit.html'  # فایل قالب ویرایش که می‌سازیم
    success_url = reverse_lazy('martyrs:martyr_list')  # یا هرجا می‌خوای بعد ویرایش بری

    def test_func(self):
        # فقط سوپر یوزر اجازه ویرایش داره
        return self.request.user.is_superuser