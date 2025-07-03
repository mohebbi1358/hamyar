

from wallet.models import Wallet, WalletTransaction
from donation.models import Donation


def process_wallet_donation(user, amount, cause_obj, martyr=None, eternal=None):
    wallet = Wallet.objects.filter(user=user).first()
    if not wallet:
        return False, "کیف پول شما فعال نیست."
    if wallet.balance < amount:
        return False, "موجودی کیف پول کافی نیست."

    wallet.balance -= amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='DONATION',
        status='SUCCESS',
        cause=cause_obj
    )

    Donation.objects.create(
        amount=amount,
        cause=cause_obj,
        status='SUCCESS',
        user=user,
        martyr=martyr,
        eternal=eternal
    )

    return True, None
