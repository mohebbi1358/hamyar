from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from martyrs.models import Martyr
from eternals.models import Eternals
from wallet.models import Wallet, WalletTransaction
from donation.models import Donation
import random


@login_required
def donate(request):
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
                return redirect('donation:donate')
        except ValueError:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donation:donate')

        if pay_method == 'wallet':
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                messages.error(request, "کیف پول شما فعال نیست.")
                return redirect('donation:donate')
            if wallet.balance < amount:
                messages.error(request, "موجودی کیف پول کافی نیست.")
                return redirect('donation:donate')

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
            return redirect('donation:fake_gateway', donation_id=donation.id)

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect('donation:donate')

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate.html', {
        'suggested_amounts': suggested_amounts,
        'martyr': martyr,
        'eternal': None,
    })


@csrf_exempt
def payment_callback(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)

    status = request.GET.get('status', 'FAILED')
    ref_id = request.GET.get('ref_id', '')
    gateway_response = str(dict(request.GET))

    donation.status = 'SUCCESS' if status == 'OK' else 'FAILED'
    donation.ref_id = ref_id
    donation.gateway_response = gateway_response
    donation.save()

    if status == 'OK':
        messages.success(request, "پرداخت با موفقیت انجام شد.")
        return redirect('home')
    else:
        messages.error(request, "پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.")
        return redirect('donation:donate')


def fake_bank_gateway(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donation/fake_gateway.html', {'donation': donation})


def fake_wallet_charge_gateway(request, wallet_tx_id):
    wallet_tx = get_object_or_404(WalletTransaction, id=wallet_tx_id)
    return redirect(f'/wallet/charge/callback/{wallet_tx.id}/?status=OK&ref_id=FAKE12345')


@login_required
def donate_for_eternal(request, eternal_id):
    eternal = get_object_or_404(Eternals, pk=eternal_id)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        pay_method = request.POST.get('pay_method')
        cause = f"صدقه برای {eternal.first_name} {eternal.last_name}"


        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donate_for_eternal', eternal_id=eternal_id)
        except ValueError:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donate_for_eternal', eternal_id=eternal_id)

        if pay_method == 'wallet':
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                messages.error(request, "کیف پول شما فعال نیست.")
                return redirect('donate_for_eternal', eternal_id=eternal_id)
            if wallet.balance < amount:
                messages.error(request, "موجودی کیف پول کافی نیست.")
                return redirect('donate_for_eternal', eternal_id=eternal_id)

            wallet.balance -= amount
            wallet.save()

            wallet_tx = WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='DONATION',
                status='SUCCESS',
                cause=cause
            )

            Donation.objects.create(
                amount=amount,
                cause='POOR',
                status='SUCCESS',
                user=request.user,
                eternal=eternal,
                wallet_transaction=wallet_tx
            )

            messages.success(request, "پرداخت از طریق کیف پول با موفقیت انجام شد.")
            return redirect('eternals:detail', pk=eternal_id)

        elif pay_method == 'gateway':
            donation = Donation.objects.create(
                amount=amount,
                cause='POOR',
                status='PENDING',
                user=request.user,
                eternal=eternal
            )
            return redirect('donation:fake_gateway', donation_id=donation.id)

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect('donate_for_eternal', eternal_id=eternal_id)

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate.html', {
        'eternal': eternal,
        'martyr': None,
        'suggested_amounts': suggested_amounts,
    })


@login_required
def donate_for_martyr(request, martyr_id):
    martyr = get_object_or_404(Martyr, pk=martyr_id)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        pay_method = request.POST.get('pay_method')
        cause = f"صدقه برای {martyr.first_name} {martyr.last_name}"

        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donation:donate_for_martyr', martyr_id=martyr_id)
        except ValueError:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donation:donate_for_martyr', martyr_id=martyr_id)

        if pay_method == 'wallet':
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                messages.error(request, "کیف پول شما فعال نیست.")
                return redirect('donation:donate_for_martyr', martyr_id=martyr_id)
            if wallet.balance < amount:
                messages.error(request, "موجودی کیف پول کافی نیست.")
                return redirect('donation:donate_for_martyr', martyr_id=martyr_id)

            wallet.balance -= amount
            wallet.save()

            wallet_tx = WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='DONATION',
                status='SUCCESS',
                cause=cause
            )

            Donation.objects.create(
                amount=amount,
                cause='POOR',
                status='SUCCESS',
                user=request.user,
                martyr=martyr,
                wallet_transaction=wallet_tx
            )

            messages.success(request, "پرداخت از طریق کیف پول با موفقیت انجام شد.")
            return redirect('wallet:wallet_transactions_report')

        elif pay_method == 'gateway':
            donation = Donation.objects.create(
                amount=amount,
                cause='POOR',
                status='PENDING',
                user=request.user,
                martyr=martyr
            )
            return redirect('donation:fake_gateway', donation_id=donation.id)

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect('donation:donate_for_martyr', martyr_id=martyr_id)

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate.html', {
        'martyr': martyr,
        'eternal': None,
        'suggested_amounts': suggested_amounts,
    })
