from django import forms
from .models import Eternals

from django import forms
from .models import Eternals


from django import forms
from .models import Eternals
import jdatetime
import datetime

class EternalsForm(forms.ModelForm):
    death_date = forms.DateField(
        label="تاریخ فوت",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        initial=datetime.date.today  # به میلادی ذخیره می‌شه ولی می‌تونی در قالب شمسی نشون بدی
    )

    class Meta:
        model = Eternals
        fields = ['first_name', 'last_name', 'known_as', 'description', 'father_name', 'death_date', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }



from django import forms
from .models import Ceremony

class CeremonyForm(forms.ModelForm):
    class Meta:
        model = Ceremony
        fields = ['ceremony']
        widgets = {
            'ceremony': forms.Textarea(attrs={'rows': 3}),
        }



from django import forms
from .models import CondolenceMessage

class CondolenceMessageForm(forms.ModelForm):
    class Meta:
        model = CondolenceMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'متن پیام تسلیت خود را بنویسید...'}),
        }






from django import forms
from .models import CondolenceMessage
from accounts.models import Persona

class CondolenceMessageForm(forms.ModelForm):
    class Meta:
        model = CondolenceMessage
        fields = ['persona', 'message']  # حذف 'eternal' چون از view تزریق میشه
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'متن پیام تسلیت را وارد کنید...'
            }),
        }
        labels = {
            'persona': 'شخصیت فرستنده',
            'message': 'متن پیام تسلیت',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # محدودسازی persona به شخصیت‌های کاربر وارد شده
        if user:
            self.fields['persona'].queryset = Persona.objects.filter(user=user)

        # اعمال کلاس CSS برای ظاهر بهتر
        self.fields['persona'].widget.attrs.update({
            'class': 'form-select'
        })
