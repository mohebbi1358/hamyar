from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import User  # اگر User سفارشی‌سازی شده است

class PhoneForm(forms.Form):
    phone = forms.CharField(label='شماره موبایل', max_length=11)

class CodeVerifyForm(forms.Form):
    code = forms.CharField(label='کد تایید', max_length=6)

class PasswordLoginForm(forms.Form):
    phone = forms.CharField(label='شماره موبایل', max_length=11)
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)

class ProfileCompletionForm(SetPasswordForm):
    first_name = forms.CharField(label='نام', max_length=30)
    last_name = forms.CharField(label='نام خانوادگی', max_length=30)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password1', 'password2']



from django import forms
from .models import User
from news.models import Category

class UserCategoryAccessForm(forms.ModelForm):
    allowed_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="دسته‌بندی‌های مجاز"
    )

    class Meta:
        model = User
        fields = ['allowed_categories']
