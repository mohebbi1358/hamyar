from django.db import models

class Donation(models.Model):
    CAUSES = [
        ('POOR', 'فقرا'),
        ('SCHOOL', 'مدرسه‌سازی'),
        ('HEALTH', 'درمان بیماران'),
    ]

    amount = models.PositiveIntegerField(verbose_name="مبلغ (تومان)")
    cause = models.CharField(max_length=20, choices=CAUSES, verbose_name="بابت")
    status = models.CharField(max_length=10, choices=[
        ('SUCCESS', 'موفق'),
        ('FAILED', 'ناموفق'),
        ('PENDING', 'در انتظار'),
    ], default='PENDING', verbose_name="وضعیت پرداخت")
    ref_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد رهگیری بانک")
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد داخلی/رسید")
    gateway_response = models.TextField(null=True, blank=True, verbose_name="پاسخ بانک")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ پرداخت")

    wallet_transaction = models.OneToOneField(
    'wallet.WalletTransaction', on_delete=models.SET_NULL,
    null=True, blank=True, related_name='donation_record'
)
    

    def __str__(self):
        return f"{self.amount} تومان - {self.get_cause_display()} - {self.status}"
