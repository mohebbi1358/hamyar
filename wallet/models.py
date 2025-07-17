# models.py
from django.db import models
from django.conf import settings
from donation.models import Donation
from donation.models import DonationCause


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.PositiveIntegerField(default=0, verbose_name="موجودی کیف پول (تومان)")

    def __str__(self):
        name_or_id = getattr(self.user, 'get_full_name', lambda: '')() or getattr(self.user, 'phone', '') or self.user.username
        return f"کیف پول {name_or_id} - موجودی: {self.balance} تومان"




class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('CHARGE', 'شارژ کیف پول'),
        ('DONATION', 'پرداخت صدقه از کیف پول'),
        ('COUPON_PURCHASE', 'خرید کوپن ارسال پیام از کیف پول'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'موفق'),
        ('FAILED', 'ناموفق'),
        ('PENDING', 'در انتظار'),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.PositiveIntegerField(verbose_name="مبلغ (تومان)")
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        default='CHARGE'
    )
    cause = models.ForeignKey(
        DonationCause,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wallet_transactions'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SUCCESS'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ref_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="شناسه مرجع تراکنش")
    
    # ✅ فیلد جدید
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="توضیحات تراکنش"
    )

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} تومان - {self.status}"




