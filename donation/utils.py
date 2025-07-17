from wallet.models import Wallet, WalletTransaction
from donation.models import Donation

def process_wallet_donation(
    user,
    amount,
    cause_obj,
    martyr=None,
    eternal=None,
    group_id=None,
    quantity=None,
    redirect_url=None
):
    wallet = Wallet.objects.filter(user=user).first()
    if not wallet:
        return False, "کیف پول شما فعال نیست.", None

    if wallet.balance < amount:
        return False, "موجودی کیف پول کافی نیست.", None

    wallet.balance -= amount
    wallet.save()

    wallet_tx = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='DONATION',
        status='SUCCESS',
        cause=cause_obj
    )

    extra_data = {}
    if group_id is not None:
        extra_data['group_id'] = group_id
    if quantity is not None:
        extra_data['quantity'] = quantity

    donation = Donation.objects.create(
        amount=amount,
        cause=cause_obj,
        status='SUCCESS',
        user=user,
        martyr=martyr,
        eternal=eternal,
        extra_data=extra_data if extra_data else None,
        wallet_transaction=wallet_tx,
        redirect_url=redirect_url,
        pay_method='wallet'   # ← این خط اضافه شد
    )

    return True, None, donation
