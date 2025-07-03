from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from martyrs.models import Martyr
from eternals.models import Eternals
from wallet.models import Wallet, WalletTransaction
from .utils import process_wallet_donation
from donation.models import Donation
import random





@login_required
def donate(request):
    causes = DonationCause.objects.filter(is_active=True)

    martyr = None
    count = Martyr.objects.count()
    if count > 0:
        martyr = Martyr.objects.all()[random.randint(0, count - 1)]

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        cause_id = request.POST.get('cause')
        pay_method = request.POST.get('pay_method')

        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donation:donate')
        except ValueError:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donation:donate')

        if not cause_id:
            messages.error(request, "لطفاً دلیل صدقه را انتخاب کنید.")
            return redirect('donation:donate')

        cause_obj = get_object_or_404(DonationCause, id=cause_id)

        if pay_method == 'wallet':
            success, error_msg = process_wallet_donation(request.user, amount, cause_obj)
            if not success:
                messages.error(request, error_msg)
                return redirect('donation:donate')

            messages.success(request, "پرداخت از طریق کیف پول با موفقیت انجام شد.")
            return redirect('wallet:wallet_transactions_report')

        elif pay_method == 'gateway':
            donation = Donation.objects.create(
                amount=amount,
                cause=cause_obj,
                status='PENDING',
                user=request.user
            )
            return redirect('donation:fake_gateway', donation_id=donation.id)

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect('donation:donate')

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate.html', {
        'causes': causes,
        'suggested_amounts': suggested_amounts,
        'martyr': martyr,
        'eternal': None,
    })


@login_required
def donate_for_eternal(request, eternal_id):
    causes = DonationCause.objects.filter(is_active=True)
    eternal = get_object_or_404(Eternals, pk=eternal_id)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        pay_method = request.POST.get('pay_method')
        cause_id = request.POST.get('cause')

        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donation:donate_for_eternal', eternal_id=eternal_id)
        except ValueError:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donation:donate_for_eternal', eternal_id=eternal_id)

        if not cause_id:
            messages.error(request, "لطفاً دلیل صدقه را انتخاب کنید.")
            return redirect('donation:donate_for_eternal', eternal_id=eternal_id)

        cause_obj = get_object_or_404(DonationCause, id=cause_id)
        # تغییر فقط متن دلیل (برای تراکنش)
        cause_text = f"{cause_obj.title} برای {eternal.first_name} {eternal.last_name}"

        if pay_method == 'wallet':
            success, error_msg = process_wallet_donation(
                request.user, amount, cause_obj, martyr=None, eternal=eternal)
            if not success:
                messages.error(request, error_msg)
                return redirect('donation:donate_for_eternal', eternal_id=eternal_id)

            messages.success(request, "پرداخت از طریق کیف پول با موفقیت انجام شد.")
            return redirect('eternals:detail', pk=eternal_id)

        elif pay_method == 'gateway':
            donation = Donation.objects.create(
                amount=amount,
                cause=cause_obj,
                status='PENDING',
                user=request.user,
                eternal=eternal
            )
            return redirect('donation:fake_gateway', donation_id=donation.id)

        else:
            messages.error(request, "روش پرداخت نامعتبر است.")
            return redirect('donation:donate_for_eternal', eternal_id=eternal_id)

    suggested_amounts = [10000, 25000, 40000, 60000, 100000]
    return render(request, 'donation/donate.html', {
        'causes': causes,
        'eternal': eternal,
        'martyr': None,
        'suggested_amounts': suggested_amounts,
    })


@login_required
def donate_for_martyr(request, martyr_id):
    causes = DonationCause.objects.filter(is_active=True)
    martyr = get_object_or_404(Martyr, pk=martyr_id)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').replace(',', '')
        pay_method = request.POST.get('pay_method')
        cause_id = request.POST.get('cause')

        try:
            amount = int(amount_str)
            if amount < 1000:
                messages.error(request, "حداقل مبلغ ۱۰۰۰ تومان است.")
                return redirect('donation:donate_for_martyr', martyr_id=martyr_id)
        except ValueError:
            messages.error(request, "مبلغ وارد شده معتبر نیست.")
            return redirect('donation:donate_for_martyr', martyr_id=martyr_id)

        if not cause_id:
            messages.error(request, "لطفاً دلیل صدقه را انتخاب کنید.")
            return redirect('donation:donate_for_martyr', martyr_id=martyr_id)

        cause_obj = get_object_or_404(DonationCause, id=cause_id)
        cause_text = f"{cause_obj.title} برای {martyr.first_name} {martyr.last_name}"

        if pay_method == 'wallet':
            success, error_msg = process_wallet_donation(
                request.user, amount, cause_obj, martyr=martyr, eternal=None)
            if not success:
                messages.error(request, error_msg)
                return redirect('donation:donate_for_martyr', martyr_id=martyr_id)

            messages.success(request, "پرداخت از طریق کیف پول با موفقیت انجام شد.")
            return redirect('wallet:wallet_transactions_report')

        elif pay_method == 'gateway':
            donation = Donation.objects.create(
                amount=amount,
                cause=cause_obj,
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
        'causes': causes,
        'martyr': martyr,
        'eternal': None,
        'suggested_amounts': suggested_amounts,
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



# donation/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import DonationCause
from .forms import DonationCauseForm

@staff_member_required
def donationcause_list(request):
    causes = DonationCause.objects.all()
    return render(request, 'donation/donationcause_list.html', {'causes': causes})

@staff_member_required
def donationcause_create(request):
    if request.method == 'POST':
        form = DonationCauseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donation:donationcause_list')
    else:
        form = DonationCauseForm()
    return render(request, 'donation/donationcause_form.html', {'form': form})

@staff_member_required
def donationcause_edit(request, pk):
    cause = get_object_or_404(DonationCause, pk=pk)
    if request.method == 'POST':
        form = DonationCauseForm(request.POST, instance=cause)
        if form.is_valid():
            form.save()
            return redirect('donation:donationcause_list')
    else:
        form = DonationCauseForm(instance=cause)
    return render(request, 'donation/donationcause_form.html', {'form': form})

@staff_member_required
def donationcause_delete(request, pk):
    cause = get_object_or_404(DonationCause, pk=pk)
    if request.method == 'POST':
        cause.delete()
        return redirect('donation:donationcause_list')
    return render(request, 'donation/donationcause_confirm_delete.html', {'cause': cause})




from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Q
from donation.models import Donation
from wallet.models import WalletTransaction



from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render
from django.utils import timezone
from wallet.models import WalletTransaction
from donation.models import Donation, DonationCause
from accounts.models import User

@login_required
@user_passes_test(lambda u: u.is_superuser)
def donation_wallet_report(request):
    donations = Donation.objects.all()
    wallet_transactions = WalletTransaction.objects.all()
    
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    donation_status = request.GET.get("donation_status")
    transaction_status = request.GET.get("transaction_status")
    cause_id = request.GET.get("cause")
    user_id = request.GET.get("user")

    # فیلتر تاریخ
    if start_date:
        donations = donations.filter(created_at__date__gte=start_date)
        wallet_transactions = wallet_transactions.filter(created_at__date__gte=start_date)
    if end_date:
        donations = donations.filter(created_at__date__lte=end_date)
        wallet_transactions = wallet_transactions.filter(created_at__date__lte=end_date)

    # فیلتر وضعیت
    if donation_status:
        donations = donations.filter(status=donation_status)
    if transaction_status:
        wallet_transactions = wallet_transactions.filter(status=transaction_status)
    
    # فیلتر علت
    if cause_id:
        donations = donations.filter(cause_id=cause_id)
        wallet_transactions = wallet_transactions.filter(cause_id=cause_id)
    
    # فیلتر کاربر
    if user_id:
        donations = donations.filter(user_id=user_id)
        wallet_transactions = wallet_transactions.filter(wallet__user_id=user_id)

    causes = DonationCause.objects.all()
    users = User.objects.all()

    # Excel export
    if request.GET.get("export") == "excel":
        return export_to_excel(donations, wallet_transactions)

    return render(request, 'donation/report.html', {
        'donations': donations,
        'wallet_transactions': wallet_transactions,
        'causes': causes,
        'users': users,
    })


import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.utils import timezone

def export_to_excel(donations, wallet_transactions):
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "صدقات"

    headers1 = ["مبلغ", "وضعیت", "علت", "کاربر", "شهید", "جاودانه", "تاریخ"]
    ws1.append(headers1)

    for d in donations:
        ws1.append([
            d.amount,
            d.get_status_display(),
            str(d.cause or ""),
            str(d.user or ""),
            str(d.martyr or ""),
            str(d.eternal or ""),
            timezone.localtime(d.created_at).strftime("%Y-%m-%d %H:%M")
        ])

    # Sheet 2: Wallet Transactions
    ws2 = wb.create_sheet(title="تراکنش‌های کیف پول")
    headers2 = ["کاربر", "نوع تراکنش", "مبلغ", "وضعیت", "علت", "تاریخ"]
    ws2.append(headers2)

    for tx in wallet_transactions:
        ws2.append([
            str(tx.wallet.user or ""),
            tx.get_transaction_type_display(),
            tx.amount,
            tx.get_status_display(),
            str(tx.cause or ""),
            timezone.localtime(tx.created_at).strftime("%Y-%m-%d %H:%M")
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"donation_wallet_report_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response
