from django import forms
from .models import Eternals

from django import forms
from .models import Eternals


from django import forms
from .models import Eternals
import jdatetime
import datetime



import jdatetime

class EternalsForm(forms.ModelForm):
    death_date = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'death_date_picker',
            'autocomplete': 'off',
            'placeholder': 'تاریخ فوت',
        })
    )

    class Meta:
        model = Eternals
        fields = ['first_name', 'last_name', 'known_as', 'description', 'father_name', 'death_date', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            if self.instance and self.instance.death_date:
                try:
                    self.fields['death_date'].initial = jdatetime.date.fromgregorian(date=self.instance.death_date).strftime('%Y/%m/%d')
                except:
                    pass

    def clean_death_date(self):
        date_str = self.cleaned_data.get('death_date')
        if date_str:
            try:
                y, m, d = map(int, date_str.replace('-', '/').split('/'))
                return jdatetime.date(y, m, d).togregorian()
            except:
                raise forms.ValidationError("تاریخ فوت نامعتبر است.")
        return None
    


    
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
