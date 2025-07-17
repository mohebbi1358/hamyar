from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from eternals.models import Eternals
from news.models import News

User = get_user_model()


class NotificationGroup(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان گروه نوتیفیکیشن")
    is_mandatory = models.BooleanField(default=False, verbose_name="اجباری است؟")
    hidden = models.BooleanField(default=False, verbose_name="مخفی است؟")
    send_cost = models.PositiveIntegerField(default=0, verbose_name="هزینه ارسال پیام (تومان)")
    needs_approval = models.BooleanField(default=False, verbose_name="نیاز به تایید مدیر دارد؟")
    is_public = models.BooleanField(default=True, verbose_name="عمومی است؟")

    managers = models.ManyToManyField(
        'accounts.User',
        related_name='managed_notification_groups',
        blank=True,
        verbose_name="مدیران گروه"
    )
    allowed_senders = models.ManyToManyField(
        'accounts.User',
        related_name='allowed_notification_groups',
        blank=True,
        verbose_name="ارسال‌کنندگان مجاز"
    )

    default_expire_days = models.PositiveIntegerField(
        default=30,
        verbose_name="مدت پیش‌فرض اعتبار پیام (روز)"
    )

    def __str__(self):
        return self.title


class NotificationCoupon(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notification_coupons',
        verbose_name="کاربر"
    )
    group = models.ForeignKey(
        NotificationGroup,
        on_delete=models.CASCADE,
        related_name='coupons',
        verbose_name="گروه نوتیفیکیشن"
    )
    quantity_purchased = models.PositiveIntegerField(verbose_name="تعداد کوپن خریداری شده")
    quantity_used = models.PositiveIntegerField(default=0, verbose_name="تعداد کوپن مصرف شده")
    quantity_reserved = models.PositiveIntegerField(default=0, verbose_name="تعداد کوپن رزرو شده")

    donation_record = models.ForeignKey(
        'donation.Donation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="رکورد پرداخت صدقه مرتبط"
    )

    @property
    def remaining(self):
        return self.quantity_purchased - self.quantity_used - self.quantity_reserved

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group.title} - باقی‌مانده: {self.remaining}"

    class Meta:
        unique_together = ('user', 'group')


class Notification(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_SENT = 'SENT'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار تایید'),
        (STATUS_APPROVED, 'تایید شده'),
        (STATUS_REJECTED, 'رد شده'),
        (STATUS_SENT, 'ارسال شده'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان پیام")
    description = models.TextField(verbose_name="توضیحات پیام")
    group = models.ForeignKey(
        NotificationGroup,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="گروه نوتیفیکیشن"
    )
    expire_days = models.PositiveIntegerField(default=30, verbose_name="مدت اعتبار پیام (روز)")
    eternal = models.ForeignKey(
        Eternals,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="جاودانه مرتبط"
    )
    news = models.ForeignKey(
        News,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="خبر مرتبط"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="ایجادکننده پیام"
    )
    coupon_reserved = models.ForeignKey(
        'notification.NotificationCoupon',  # اشاره به صورت رشته‌ای برای جلوگیری از ImportError
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کوپن رزروشده"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="وضعیت"
    )
    is_sent = models.BooleanField(default=False, verbose_name="ارسال شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def clean(self):
        if self.eternal_id and self.news_id:
            raise ValidationError("نمی‌توانید همزمان هم جاودانه و هم خبر را به یک پیام مرتبط کنید.")

    def __str__(self):
        return self.title


class NotificationSeen(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='seen_records',
        verbose_name="نوتیفیکیشن"
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications_seen',
        verbose_name="کاربر"
    )
    seen_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ مشاهده")

    class Meta:
        unique_together = ('notification', 'user')


class NotificationGroupMembership(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notification_memberships'
    )
    group = models.ForeignKey(
        NotificationGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group.title}"


class NotificationCouponPurchase(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("wallet", "Wallet"),
        ("bank", "Bank"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(NotificationGroup, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    donation = models.ForeignKey("donation.Donation", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user} bought {self.quantity} coupons from {self.group.title}"
