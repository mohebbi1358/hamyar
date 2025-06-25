from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Donation
from wallet.models import Wallet, WalletTransaction
from django.contrib import messages
from martyrs.models import Martyr  # اضافه کن
import random  # اضافه کن



@login_required
def donate(request):
    # انتخاب شهید رندوم
    martyr = None
    count = Martyr.objects.count()
    if count > 0:
        martyr = Martyr.objects.all()[random.randint(0, count - 1)]

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        cause = request.POST.get('cause')
        pay_method = request.POST.get('pay_method')

        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donate')
        except:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donate')

        if pay_method == 'wallet':
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                messages.error(request, "کیف پول شما فعال نیست.")
                return redirect('donate')
            if wallet.balance < amount:
                messages.error(request, "موجودی کیف پول کافی نیست.")
                return redirect('donate')

            wallet.balance -= amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='DONATION',
                status='SUCCESS',
                cause=cause
            )

            messages.success(request, "پرداخت از طریق کیف پول با موفقیت انجام شد.")
            return redirect('wallet:wallet_transactions_report')

        elif pay_method == 'gateway':
            donation = Donation.objects.create(
                amount=amount,
                cause=cause,
                status='PENDING'
            )
            return redirect('fake_gateway', donation_id=donation.id)

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect('donate')

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate.html', {
        'suggested_amounts': suggested_amounts,
        'martyr': martyr  # اضافه شده
    })



@csrf_exempt
def payment_callback(request, donation_id):
    donation = Donation.objects.get(id=donation_id)

    status = request.GET.get('status', 'FAILED')
    ref_id = request.GET.get('ref_id', '')
    gateway_response = str(dict(request.GET))

    # ذخیره وضعیت پرداخت در دیتابیس
    donation.status = 'SUCCESS' if status == 'OK' else 'FAILED'
    donation.ref_id = ref_id
    donation.gateway_response = gateway_response
    donation.save()

    # بررسی موفقیت یا شکست پرداخت
    if status == 'OK':
        messages.success(request, "پرداخت با موفقیت انجام شد.")
        return redirect('home')  # فرض بر اینکه نام URL صفحه اصلی "home" هست
    else:
        messages.error(request, "پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.")
        return redirect('donate')



def fake_bank_gateway(request, donation_id):
    """شبیه‌سازی صفحه پرداخت بانکی برای صدقه"""
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donation/fake_gateway.html', {'donation': donation})



from django.shortcuts import get_object_or_404, redirect
from wallet.models import WalletTransaction

def fake_wallet_charge_gateway(request, wallet_tx_id):
    # گرفتن تراکنش شارژ کیف پول
    wallet_tx = get_object_or_404(WalletTransaction, id=wallet_tx_id)

    # در اینجا می‌توانی یک صفحه نمایش بدی که کاربر پرداخت را تایید کند.
    # برای سادگی مستقیم ریدایرکت می‌کنیم به callback کیف پول با وضعیت موفق.

    return redirect(f'/wallet/charge/callback/{wallet_tx.id}/?status=OK&ref_id=FAKE12345')



@login_required
def donate_for_eternal(request, eternal_id):
    eternal = get_object_or_404(Eternals, pk=eternal_id)
    
    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        pay_method = request.POST.get('pay_method')
        cause = f"صدقه برای {eternal.name}"  # یا هر فیلدی که اسم اترنال رو داره

        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donations:donate_for_eternal', eternal_id=eternal_id)
        except:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donations:donate_for_eternal', eternal_id=eternal_id)

        # کد پرداخت مشابه ویوی donate که قبلاً نوشتی
        # مثلا با کیف پول یا درگاه بانکی...

        # برای نمونه فقط پیام موفقیت:
        messages.success(request, f"صدقه برای {eternal.name} ثبت شد.")
        return redirect('eternals:detail', pk=eternal_id)

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate_for_eternal.html', {
        'eternal': eternal,
        'suggested_amounts': suggested_amounts,
    })