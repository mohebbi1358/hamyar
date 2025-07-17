# notification/forms.py

from django import forms
from .models import Notification, NotificationGroup






from django import forms
from .models import Notification








from eternals.models import Eternals
from news.models import News




from django import forms
from eternals.models import Eternals
from news.models import News
from .models import Notification










from django import forms
from .models import Notification
from eternals.models import Eternals
from news.models import News





from django import forms
from .models import Notification, NotificationGroup



from django import forms
from .models import Notification, NotificationGroup




class NotificationCreateForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=NotificationGroup.objects.none(),
        label="گروه"
    )

    class Meta:
        model = Notification
        fields = ['group', 'title', 'description', 'expire_days', 'eternal', 'news']
        widgets = {
            'description': forms.Textarea(attrs={'maxlength': 250}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # مقداردهی expire_days بر اساس گروه انتخاب شده
        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                group = NotificationGroup.objects.get(pk=group_id)
                self.fields['expire_days'].initial = group.default_expire_days
            except (ValueError, NotificationGroup.DoesNotExist):
                pass
        elif self.instance.pk:
            self.fields['expire_days'].initial = self.instance.expire_days
        else:
            self.fields['expire_days'].initial = 30

    def clean(self):
        cleaned_data = super().clean()
        eternal = cleaned_data.get('eternal')
        news = cleaned_data.get('news')
        if eternal and news:
            raise forms.ValidationError("نمی‌توانید همزمان هم جاودانه و هم خبر را انتخاب کنید.")
        return cleaned_data



























# notification/forms.py (ادامه)

class BuyCouponForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=NotificationGroup.objects.filter(send_cost__gt=0),
        label="گروه نوتیفیکیشن"
    )
    quantity = forms.IntegerField(min_value=1, label="تعداد کوپن")




from django import forms
from .models import NotificationGroup, NotificationGroupMembership

class NotificationSettingsForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=NotificationGroup.objects.filter(is_mandatory=False, hidden=False),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="گروه‌های پیام اختیاری"
    )




from django import forms
from .models import NotificationGroup
from accounts.models import User













# forms.py

from django import forms
from django.contrib.auth import get_user_model
from .models import NotificationGroup, NotificationGroupMembership

User = get_user_model()

class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.get_display_name()} - {obj.phone}"

class NotificationGroupForm(forms.ModelForm):
    allowed_senders = UserMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control user-select'}),
        required=False,
        label="ارسال‌کنندگان مجاز"
    )

    managers = UserMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control user-select'}),
        required=False,
        label="مدیران گروه"
    )

    members = UserMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control user-select'}),
        required=False,
        label="اعضای گروه"
    )

    class Meta:
        model = NotificationGroup
        fields = [
            'title',
            'is_mandatory',
            'hidden',
            'send_cost',
            'needs_approval',
            'is_public',
            'allowed_senders',
            'managers',
            'default_expire_days',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'send_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_mandatory': forms.CheckboxInput(),
            'hidden': forms.CheckboxInput(),
            'needs_approval': forms.CheckboxInput(),
            'is_public': forms.CheckboxInput(),
            'default_expire_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            # پر کردن اولیه اعضای گروه
            self.fields['members'].initial = instance.memberships.values_list('user_id', flat=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()

            # ذخیره کردن اعضای گروه
            members = self.cleaned_data.get('members')
            if members is not None:
                # حذف اعضای قبلی
                NotificationGroupMembership.objects.filter(group=instance).exclude(user__in=members).delete()

                # اضافه‌کردن اعضای جدید
                existing_ids = NotificationGroupMembership.objects.filter(group=instance).values_list('user_id', flat=True)
                for user in members:
                    if user.id not in existing_ids:
                        NotificationGroupMembership.objects.create(group=instance, user=user)

        return instance














from django.db.models import Q
from django import forms

class NotificationCreateHidden(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=NotificationGroup.objects.none(),
        label="گروه"
    )

    class Meta:
        model = Notification
        fields = ['group', 'title', 'description', 'expire_days', 'eternal', 'news']
        widgets = {
            'description': forms.Textarea(attrs={'maxlength': 250}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['group'].queryset = NotificationGroup.objects.filter(
                Q(hidden=True, is_public=True) | Q(hidden=True, allowed_senders=user)
            ).distinct()
        else:
            self.fields['group'].queryset = NotificationGroup.objects.none()

        # مقداردهی expire_days بر اساس گروه انتخاب شده
        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                group = NotificationGroup.objects.get(pk=group_id)
                self.fields['expire_days'].initial = group.default_expire_days
            except (ValueError, NotificationGroup.DoesNotExist):
                pass
        elif self.instance.pk:
            self.fields['expire_days'].initial = self.instance.expire_days
        else:
            self.fields['expire_days'].initial = 30

    def clean(self):
        cleaned_data = super().clean()
        eternal = cleaned_data.get('eternal')
        news = cleaned_data.get('news')
        if eternal and news:
            raise forms.ValidationError("نمی‌توانید همزمان هم جاودانه و هم خبر را انتخاب کنید.")
        return cleaned_data





