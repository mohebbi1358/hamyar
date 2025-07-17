from donation.models import Donation




def buy_notification_coupons(user, group, quantity, cause):
    print(">>> گروه:", group.title)
    print(">>> هزینه ثبت‌شده در group.send_cost:", group.send_cost)
    
    amount = group.send_cost * quantity

    donation = Donation.objects.create(
        user=user,
        amount=amount,
        status='PENDING',
        cause=cause,
        extra_data={
            'group_id': group.id,
            'quantity': quantity,
        }
    )

    return donation
















from notification.models import NotificationCoupon, NotificationCouponPurchase, NotificationGroup





def confirm_notification_coupon_purchase(donation, payment_method):
    print(f"confirm_notification_coupon_purchase called for donation {donation.id} with status {donation.status}")
    if donation.status == 'SUCCESS':
        extra = donation.extra_data or {}
        group_id = extra.get('group_id')
        quantity = extra.get('quantity')
        print(f"Extra data: group_id={group_id}, quantity={quantity}")

        if group_id and quantity:
            group = NotificationGroup.objects.get(id=group_id)
            purchase = NotificationCouponPurchase.objects.create(
                user=donation.user,
                group=group,
                quantity=quantity,
                payment_method=payment_method,
                amount=donation.amount,
                donation=donation,
            )
            print(f"NotificationCouponPurchase created with id {purchase.id}")

            coupon, created = NotificationCoupon.objects.get_or_create(
                user=donation.user,
                group=group,
                defaults={'quantity_purchased': 0, 'quantity_used': 0}
            )
            coupon.quantity_purchased += quantity
            coupon.save()

            print("✅ کوپن ساخته یا آپدیت شد.")
            return purchase
        else:
            print("Error: group_id or quantity missing in donation.extra_data")
    else:
        print(f"Donation status is not SUCCESS, it's {donation.status}")







