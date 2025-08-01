from django.db import models
from django.core.exceptions import ValidationError
from martyrs.models import Martyr
from eternals.models import Eternals
from accounts.models import User

# donation/models.py

from django.db import models
from django.core.exceptions import ValidationError
from martyrs.models import Martyr
from eternals.models import Eternals


from accounts.models import User



# donation/models.py

from django.db import models
from django.utils.text import slugify



from django.utils.text import slugify
from django.db import models

class DonationCause(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name="کد (انگلیسی یا لاتین)"
    )
    title = models.CharField(
        max_length=100,
        verbose_name="عنوان (فارسی)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال است؟"
    )
    
    is_system = models.BooleanField(
        default=False,
        verbose_name="سیستمی (برای استفاده داخلی سایت)"
    )

    def save(self, *args, **kwargs):
        if not self.code:
            base_code = slugify(self.title, allow_unicode=True)
            code = base_code or "cause"
            counter = 1
            while DonationCause.objects.filter(code=code).exclude(pk=self.pk).exists():
                code = f"{base_code}-{counter}"
                counter += 1
            self.code = code

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "علت صدقه"
        verbose_name_plural = "علل صدقه"









from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from donation.models import DonationCause

User = get_user_model()










from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()





from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Donation(models.Model):
    amount = models.PositiveIntegerField(verbose_name="مبلغ (تومان)")

    cause = models.ForeignKey(
        'donation.DonationCause',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="بابت",
        related_name="donations"
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('SUCCESS', 'موفق'),
            ('FAILED', 'ناموفق'),
            ('PENDING', 'در انتظار'),
        ],
        default='PENDING',
        verbose_name="وضعیت پرداخت"
    )

    ref_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد رهگیری بانک")
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد داخلی/رسید")
    gateway_response = models.TextField(null=True, blank=True, verbose_name="پاسخ بانک")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ پرداخت")

    wallet_transaction = models.OneToOneField(
        'wallet.WalletTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donation_record'
    )

    eternal = models.ForeignKey(
        'eternals.Eternals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="جاودانه مرتبط",
        related_name="donations"
    )

    martyr = models.ForeignKey(
        'martyrs.Martyr',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="شهید مرتبط",
        related_name="donations"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کاربر پرداخت‌کننده",
        related_name="donations"
    )
    PAY_METHOD_CHOICES = [
        ('wallet', 'Wallet'),
        ('gateway', 'Gateway'),
    ]

    pay_method = models.CharField(
        max_length=20,
        choices=PAY_METHOD_CHOICES,
        null=True,
        blank=True,
        verbose_name="روش پرداخت"
    )

    extra_data = models.JSONField(null=True, blank=True, verbose_name="داده‌های اضافی")
    redirect_url = models.CharField(max_length=500, null=True, blank=True)


    def clean(self):
        if not self.martyr and not self.eternal:
            raise ValidationError("صدقه باید از طرف یک شهید یا یک جاودانه باشد.")
        if self.martyr and self.eternal:
            raise ValidationError("صدقه نمی‌تواند همزمان هم از طرف شهید و هم از طرف جاودانه باشد.")

    def __str__(self):
        cause_title = self.cause.title if self.cause else "-"
        title = f"{self.amount} تومان - {cause_title} - {self.status}"
        if self.user:
            title += f" - توسط: {self.user.get_full_name() or self.user.username}"
        if self.martyr:
            title += f" - شهید: {self.martyr}"
        elif self.eternal:
            title += f" - جاودانه: {self.eternal}"
        return title

    class Meta:
        verbose_name = "صدقه"
        verbose_name_plural = "صدقات"
        ordering = ['-created_at']











