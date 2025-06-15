# wallet/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, WalletTransaction
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

@login_required
def charge_wallet(request):
    if request.method == 'POST':
        try:
            amount = int(request.POST['amount'].replace(',', ''))  # پاک کردن کاماها
        except (KeyError, ValueError):
            messages.error(request, "مبلغ نامعتبر است.")
            return redirect('wallet:charge_wallet')

        user_wallet, _ = Wallet.objects.get_or_create(user=request.user)

        wallet_tx = WalletTransaction.objects.create(
            wallet=user_wallet,
            amount=amount,
            transaction_type='CHARGE',
            status='PENDING'
        )

        # ✅ مسیر درست برگشت به درگاه فیک
        return redirect(reverse('wallet:fake_wallet_charge_gateway', kwargs={'wallet_tx_id': wallet_tx.id}))

    return render(request, 'wallet/charge_wallet.html')


@csrf_exempt
@login_required
def wallet_charge_callback(request, wallet_tx_id):
    wallet_tx = get_object_or_404(
        WalletTransaction,
        id=wallet_tx_id,
        wallet__user=request.user,
        transaction_type='CHARGE'
    )

    status = request.GET.get('status', 'FAILED')
    ref_id = request.GET.get('ref_id', '')

    wallet_tx.status = 'SUCCESS' if status == 'OK' else 'FAILED'
    wallet_tx.ref_id = ref_id
    wallet_tx.save()

    if status not in ['OK', 'FAILED']:
        messages.error(request, "وضعیت بازگشتی از درگاه نامعتبر است.")
        return render(request, 'wallet/result.html', {'donation': wallet_tx})

    if wallet_tx.status == 'SUCCESS':
        wallet = wallet_tx.wallet
        wallet.balance += wallet_tx.amount
        wallet.save()
        messages.success(request, "شارژ کیف پول با موفقیت انجام شد.")
        return redirect('wallet:wallet_transactions_report')
    else:
        messages.error(request, "پرداخت ناموفق بود.")
        return render(request, 'wallet/result.html', {'donation': wallet_tx})  # 👈 تغییر این خط










@login_required
def donate_from_wallet(request):
    user_wallet = Wallet.objects.filter(user=request.user).first()
    if not user_wallet:
        messages.error(request, "کیف پول شما فعال نیست. ابتدا آن را شارژ کنید.")
        return redirect('wallet:charge_wallet')

    if request.method == 'POST':
        amount = int(request.POST['amount'])
        cause = request.POST['cause']

        if user_wallet.balance < amount:
            messages.error(request, "موجودی کیف پول کافی نیست.")
            return redirect('wallet:donate_from_wallet')

        wallet_tx = WalletTransaction.objects.create(
            wallet=user_wallet,
            amount=amount,
            transaction_type='DONATION',
            cause=cause,
            status='SUCCESS'
        )

        user_wallet.balance -= amount
        user_wallet.save()

        messages.success(request, "صدقه با موفقیت پرداخت شد.")
        return redirect('wallet:wallet_transactions_report')

    return render(request, 'donation/donate_from_wallet.html', {'wallet': user_wallet})


from django.core.paginator import Paginator

@login_required
def wallet_transactions_report(request):
    wallet = Wallet.objects.filter(user=request.user).first()
    if not wallet:
        return render(request, 'wallet/wallet_report.html', {
            'latest_tx': None,
            'wallet': None,
            'page_obj': [],
        })

    all_transactions = wallet.transactions.order_by('-created_at')

    # ساخت لیست شامل هر تراکنش همراه با مانده بعد از آن
    tx_with_balances = []
    balance = wallet.balance

    for tx in all_transactions:
        tx_with_balances.append({
            'tx': tx,
            'balance_after': balance
        })
        if tx.status == 'SUCCESS':
            if tx.transaction_type == 'CHARGE':
                balance -= tx.amount
            elif tx.transaction_type == 'DONATION':
                balance += tx.amount

    # صفحه‌بندی
    paginator = Paginator(tx_with_balances, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'wallet/wallet_report.html', {
        'wallet': wallet,
        'latest_tx': all_transactions.first(),
        'page_obj': page_obj,
    })



@login_required
def wallet_dashboard(request):
    wallet = Wallet.objects.filter(user=request.user).first()
    transactions = wallet.transactions.order_by('-created_at') if wallet else []
    return render(request, 'wallet/dashboard.html', {
        'wallet': wallet,
        'transactions': transactions,
    })


def fake_wallet_charge_gateway(request, wallet_tx_id):
    wallet_tx = get_object_or_404(WalletTransaction, id=wallet_tx_id)
    return render(request, 'wallet/fake_wallet_gateway.html', {'wallet_tx': wallet_tx})
