from django.db import models

from django.db import models


from django.db import models

class Eternals(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    known_as = models.CharField(max_length=100, verbose_name="معروف به", blank=True, null=True)
    father_name = models.CharField(max_length=100, verbose_name="نام پدر", blank=True, null=True)
    description = models.TextField(verbose_name="توضیحات", blank=True, null=True)
    
    # ✅ فیلد تاریخ فوت که برگردونده شده
    death_date = models.DateField(verbose_name="تاریخ فوت", blank=True, null=True)

    image = models.ImageField(upload_to='eternals/', null=True, blank=True, verbose_name="تصویر")

    created_at = models.DateTimeField(auto_now_add=True)  # اگر هنوز نداری، برای مرتب‌سازی خیلی مفیده

    class Meta:
        verbose_name = "جاودانه"
        verbose_name_plural = "جاودانه‌ها"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"






from django.db import models
from accounts.models import Persona
from django.conf import settings

class Ceremony(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ceremonies')
    eternal = models.ForeignKey(Eternals, on_delete=models.CASCADE, related_name='ceremonies')  # اضافه شد
    ceremony = models.TextField(verbose_name="مراسم")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"مراسم ثبت شده توسط {self.user.get_display_name()}"


class CondolenceMessage(models.Model):
    eternal = models.ForeignKey(Eternals, on_delete=models.CASCADE, related_name='condolences')  # اضافه شد
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='condolences')
    message = models.TextField(verbose_name="متن پیام تسلیت")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"پیام از طرف {self.persona.name}"
