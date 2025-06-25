from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from accounts.models import Persona

class Martyr(models.Model):
    first_name = models.CharField("نام", max_length=50)
    last_name = models.CharField("نام خانوادگی", max_length=50)
    father_name = models.CharField("نام پدر", max_length=50, blank=True, null=True)
    birth_place = models.CharField("محل تولد", max_length=100, blank=True, null=True)
    birth_date = models.DateField("تاریخ تولد", blank=True, null=True)
    last_operation = models.CharField("آخرین عملیات", max_length=100, blank=True, null=True)
    martyr_region = models.CharField("منطقه شهادت", max_length=100, blank=True, null=True)
    martyr_place = models.CharField("محل شهادت", max_length=100, blank=True, null=True)
    martyr_date = models.DateField("تاریخ شهادت", blank=True, null=True)
    grave_place = models.CharField("محل دفن", max_length=150, blank=True, null=True)
    photo = models.ImageField("عکس شهید", upload_to='martyrs/photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "شهید"
        verbose_name_plural = "شهدا"
        ordering = ["last_name", "first_name"]


class MartyrMemory(models.Model):
    martyr = models.ForeignKey(Martyr, on_delete=models.CASCADE, related_name='memories', verbose_name="شهید مربوطه")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر ارسال‌کننده")
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="شخصیت ارسال‌کننده")
    text = models.TextField("دل‌نوشته", blank=True, null=True)
    audio = models.FileField("فایل صوتی", upload_to='memories/audio/', blank=True, null=True)
    image = models.ImageField("تصویر", upload_to='memories/images/', blank=True, null=True)

    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    def __str__(self):
        return f"خاطره از {self.user} برای {self.martyr}"

    class Meta:
        verbose_name = "خاطره شهید"
        verbose_name_plural = "خاطرات شهدا"
        ordering = ['-created_at']

    def clean(self):
        if not self.text and not self.audio and not self.image:
            raise ValidationError("حداقل یکی از دل‌نوشته، صوت یا تصویر باید وارد شود.")
