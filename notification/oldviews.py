

from django.db import models
from notification.models import NotificationCoupon, NotificationCouponPurchase
from wallet.models import Wallet, WalletTransaction

from .models import NotificationSeen
from donation.models import Donation
from django.shortcuts import render
from donation.models import Donation


# Create your views here.
# notification/views.py

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import NotificationCreateForm, BuyCouponForm
from .models import Notification, NotificationCoupon, NotificationGroup
from django.db.models import Q






# views.py












from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .forms import NotificationCreateForm
from .models import NotificationGroup, NotificationCoupon




from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, IntegerField, Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import NotificationGroup, Notification, NotificationCoupon, Eternals, News
from .forms import NotificationCreateForm
from django.core.exceptions import ValidationError

@login_required
def create_notification(request):
    user = request.user

    # گروه‌هایی که کاربر اجازه ارسال دارد (عمومی یا گروه‌های مجاز)
    groups = NotificationGroup.objects.filter(
        Q(is_public=True) | Q(allowed_senders=user)
    ).filter(hidden=False)

    if request.method == 'POST':
        form = NotificationCreateForm(request.POST)
        form.fields['group'].queryset = groups  # محدود کردن گروه‌ها به کاربر در فرم

        if form.is_valid():
            notif = form.save(commit=False)
            notif.created_by = user

            # چک اجازه ارسال در گروه انتخابی
            if notif.group not in groups:
                messages.error(request, "شما اجازه ارسال پیام در این گروه را ندارید.")
                return redirect('notification:create_notification')

            # چک کوپن اگر گروه پولی است (send_cost > 0)
            if notif.group.send_cost > 0:
                user_coupons = NotificationCoupon.objects.filter(user=user, group=notif.group)
                total_remaining = user_coupons.aggregate(
                    total_remaining=Sum(
                        ExpressionWrapper(F('quantity_purchased') - F('quantity_used'), output_field=IntegerField())
                    )
                )['total_remaining'] or 0

                if total_remaining <= 0:
                    messages.error(request, "برای ارسال پیام در این گروه باید کوپن ارسال پیام تهیه نمایید.")
                    return redirect('notification:create_notification')

            # تنظیم فیلدهای eternal و news از داده‌های POST
            eternal_id = request.POST.get('eternal')
            news_id = request.POST.get('news')

            if eternal_id:
                try:
                    notif.eternal = Eternals.objects.get(id=eternal_id)
                except Eternals.DoesNotExist:
                    notif.eternal = None

            if news_id:
                try:
                    notif.news = News.objects.get(id=news_id)
                except News.DoesNotExist:
                    notif.news = None

            # Validation مدل clean
            try:
                notif.clean()
            except ValidationError as e:
                form.add_error(None, e)
                return render(request, 'notification/create_notification.html', {'form': form})

            notif.save()

            messages.success(request, "پیام با موفقیت ثبت شد.")
            return redirect('notification:notifications_list')
    else:
        initial = {}
        group_id = request.GET.get('group')
        if group_id:
            try:
                group = NotificationGroup.objects.get(id=group_id)
                initial['group'] = group
                initial['expire_days'] = group.default_expire_days or 30
            except NotificationGroup.DoesNotExist:
                initial['expire_days'] = 30
        else:
            initial['expire_days'] = 30

        form = NotificationCreateForm(initial=initial)
        form.fields['group'].queryset = groups

    return render(request, 'notification/create_notification.html', {
        'form': form
    })



















from django.urls import reverse



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BuyCouponForm
from donation.models import DonationCause
from .services import buy_notification_coupons








from django.views.decorators.csrf import csrf_exempt


















from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from donation.models import Donation, DonationCause
from wallet.models import Wallet, WalletTransaction
from .forms import BuyCouponForm
from .models import NotificationCoupon, NotificationGroup






from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from wallet.models import Wallet, WalletTransaction
from notification.models import NotificationCoupon
from notification.forms import BuyCouponForm











from donation.models import DonationCause
from notification.services import buy_notification_coupons




from donation.models import DonationCause
from notification.services import buy_notification_coupons, confirm_notification_coupon_purchase

@login_required
def buy_coupon(request):
    wallet = Wallet.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = BuyCouponForm(request.POST)

        if form.is_valid():
            group = form.cleaned_data["group"]
            quantity = form.cleaned_data["quantity"]
            total_amount = group.send_cost * quantity

            pay_method = request.POST.get("pay_method")

            try:
                cause = DonationCause.objects.get(title="خرید کوپن ارسال پیام")
            except DonationCause.DoesNotExist:
                messages.error(request, "علت پرداخت خرید کوپن تعریف نشده است.")
                return redirect("notification:buy_coupon")

            if pay_method == "wallet":
                if wallet and wallet.balance >= total_amount:
                    wallet.balance -= total_amount
                    wallet.save()

                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=total_amount,
                        description=f"خرید {quantity} کوپن از گروه {group.title}",
                        transaction_type="debit",
                    )

                    donation = buy_notification_coupons(
                        user=request.user,
                        group=group,
                        quantity=quantity,
                        cause=cause,
                    )
                    donation.status = 'SUCCESS'
                    donation.save()

                    confirm_notification_coupon_purchase(donation, payment_method="wallet")

                    messages.success(request, "خرید کوپن با موفقیت از کیف پول انجام شد.")
                    return redirect("notification:coupon-list")
                else:
                    messages.error(request, "موجودی کیف پول کافی نیست.")
            else:
                # پرداخت بانکی
                donation = buy_notification_coupons(
                    user=request.user,
                    group=group,
                    quantity=quantity,
                    cause=cause,
                )

                return redirect('donation:fake_gateway', donation_id=donation.id)
    else:
        form = BuyCouponForm()

    context = {
        "form": form,
        "wallet": wallet,
    }

    return render(request, "notification/buy_coupon.html", context)
























def delete_assign_coupons_to_user(user, group_id, quantity):
    group = NotificationGroup.objects.get(id=group_id)

    coupon, created = NotificationCoupon.objects.get_or_create(
        user=user,
        group=group,
        defaults={
            'quantity_purchased': quantity,
            'quantity_used': 0,
        }
    )
    if not created:
        coupon.quantity_purchased += quantity
        coupon.save()



















from notification.services import confirm_notification_coupon_purchase




@csrf_exempt
def delete_payment_callback(request, donation_id):
    print("notification \ CALLBACK CALLED")
    print("status:", request.GET.get('status'))
    print("ref_id:", request.GET.get('ref_id'))

    print(f"Payment callback received for donation_id={donation_id}")
    donation = get_object_or_404(Donation, id=donation_id)
    status = request.GET.get('status', 'FAILED')
    ref_id = request.GET.get('ref_id', '')
    print(f"Payment status={status}, ref_id={ref_id}")

    donation.status = 'SUCCESS' if status == 'OK' else 'FAILED'
    donation.ref_id = ref_id
    donation.save()

    if status == 'OK':
        try:
            confirm_notification_coupon_purchase(donation, payment_method="bank")
            print("Coupon purchase confirmed after payment.")
            messages.success(request, "پرداخت موفق بود و کوپن‌ها به حساب شما اضافه شدند.")
        except Exception as e:
            print(f"Error confirming coupon purchase: {e}")
            messages.error(request, f"خطا در ایجاد کوپن: {str(e)}")
        return redirect('notification:notifications_list')
    else:
        messages.error(request, "پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.")
        return redirect('notification:buy_coupon')













from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from notification.models import Notification, NotificationSeen







@login_required
def notifications_list(request):
    user = request.user

    # گروه هایی که کاربر عضو آن است و مخفی نیستند
    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        hidden=False
    )

    # گرفتن نوتیفیکیشن‌ها در این گروه‌ها با شرایط زیر:
    # اگر نیاز به تایید نیست، همه پیام‌ها را بگیر
    # اگر نیاز به تایید هست، فقط پیام‌های تایید شده را بگیر
    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False) | Q(group__needs_approval=True, status=Notification.STATUS_APPROVED)
    ).order_by('-created_at')

    return render(request, 'notification/notifications_list.html', {
        'notifications': notifications
    })




















@login_required
def notification_detail(request, pk):
    notif = get_object_or_404(Notification, pk=pk)

    # check if user allowed to see
    if notif.group.hidden:
        return redirect('notification:notifications_list')

    # ثبت دیده شدن
    from .models import NotificationSeen
    NotificationSeen.objects.get_or_create(
        user=request.user,
        notification=notif
    )

    return render(request, 'notification/notification_detail.html', {
        'notification': notif
    })






from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import NotificationGroup, NotificationGroupMembership
from .forms import NotificationSettingsForm

@login_required
def notification_settings(request):
    user = request.user

    # گروه‌های اختیاری و غیر مخفی
    all_groups = NotificationGroup.objects.filter(is_mandatory=False, hidden=False)

    # گروه‌هایی که کاربر الان عضوشونه
    user_groups = NotificationGroup.objects.filter(
        memberships__user=user
    )

    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST)
        if form.is_valid():
            selected_groups = form.cleaned_data['groups']

            # پاک کردن عضویت‌های قبلی
            NotificationGroupMembership.objects.filter(user=user).delete()

            # ذخیره عضویت‌های جدید
            for group in selected_groups:
                NotificationGroupMembership.objects.create(user=user, group=group)

            return redirect('notification:notification_settings')
    else:
        form = NotificationSettingsForm(initial={
            'groups': user_groups
        })

    context = {
        'form': form
    }
    return render(request, 'notification/notification_settings.html', context)



from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import NotificationGroup
from .forms import NotificationGroupForm

# فقط سوپر یوزر دسترسی داشته باشد
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def notification_group_list(request):
    groups = NotificationGroup.objects.all()
    return render(request, 'notification/group_list.html', {'groups': groups})



@superuser_required
def notification_group_create(request):
    if request.method == 'POST':
        form = NotificationGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            return redirect('notification:notification_group_list')
    else:
        form = NotificationGroupForm()

    return render(request, 'notification/group_form.html', {'form': form, 'is_new': True})



@superuser_required
def notification_group_edit(request, pk):
    group = get_object_or_404(NotificationGroup, pk=pk)

    if request.method == 'POST':
        form = NotificationGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('notification:notification_group_list')
    else:
        form = NotificationGroupForm(instance=group)

    return render(request, 'notification/group_form.html', {'form': form, 'is_new': False})



@superuser_required
def notification_group_delete(request, pk):
    group = get_object_or_404(NotificationGroup, pk=pk)
    group.delete()
    return redirect('notification:notification_group_list')




from django.db.models import Q








from django.utils import timezone
from datetime import timedelta





from django.utils import timezone
from datetime import timedelta





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta




from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

@login_required
def unread_notifications_list(request):
    user = request.user

    # گروه‌هایی که کاربر عضو آن است و مخفی نیستند
    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        hidden=False
    )

    # پیام‌هایی که در این گروه‌ها هستند و وضعیت مناسب دارند (ارسال شده یا تایید شده)
    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False) | Q(group__needs_approval=True, status=Notification.STATUS_APPROVED)
    )

    # شناسه پیام‌هایی که کاربر دیده است
    seen_notifications = NotificationSeen.objects.filter(user=user).values_list('notification_id', flat=True)

    now = timezone.now()

    # حذف پیام‌های منقضی شده (expire_days ممکن است None باشد)
    valid_notifications = [
        n for n in notifications
        if (n.expire_days is None) or (n.created_at + timedelta(days=n.expire_days) > now)
    ]

    # پیام‌های نخوانده: پیام‌هایی که در valid_notifications هستند ولی در seen_notifications نیستند
    unread_notifications = [
        n for n in valid_notifications if n.id not in seen_notifications
    ]

    # مرتب سازی نزولی بر اساس تاریخ ایجاد
    unread_notifications.sort(key=lambda x: x.created_at, reverse=True)

    return render(request, 'notification/unread_notifications_list.html', {
        'notifications': unread_notifications
    })














# notification/views.py



from django.http import JsonResponse
from django.views.decorators.http import require_GET
from eternals.models import Eternals
from news.models import News




# notification/views.py

from django.http import JsonResponse
from django.db.models import Q
from eternals.models import Eternals

def ajax_search_eternals(request):
    q = request.GET.get('q', '')

    eternals = Eternals.objects.all()

    if q:
        for word in q.strip().split():
            eternals = eternals.filter(
                Q(first_name__icontains=word) | Q(last_name__icontains=word)
            )

    eternals = eternals.order_by('-created_at')[:20]

    data = {
        "results": [
            {
                "id": e.id,
                "text": f"{e.first_name} {e.last_name}"
            } for e in eternals
        ]
    }
    return JsonResponse(data)





@require_GET
def ajax_search_news(request):
    q = request.GET.get('q', '')
    results = []
    if q:
        qs = News.objects.filter(title__icontains=q).order_by('-created_at')[:20]
        for news in qs:
            results.append({
                'id': news.id,
                'text': news.title
            })
    return JsonResponse({'results': results})







from django.http import JsonResponse
from django.views import View
from .models import NotificationGroup

class NotificationGroupDetailView(View):
    def get(self, request, pk):
        try:
            group = NotificationGroup.objects.get(pk=pk)
            return JsonResponse({'default_expire_days': group.default_expire_days})
        except NotificationGroup.DoesNotExist:
            return JsonResponse({'default_expire_days': 30})
        




# notification/views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Notification, NotificationSeen, NotificationGroup
from django.db.models import Q

@login_required
def unread_notifications_count(request):
    user = request.user

    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        hidden=False
    )

    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False) |
        Q(group__needs_approval=True, status=Notification.STATUS_APPROVED)
    )

    seen_notifications = NotificationSeen.objects.filter(
        user=user
    ).values_list('notification_id', flat=True)

    now = timezone.now()

    valid_notifications = [
        n for n in notifications
        if (n.expire_days is None) or (n.created_at + timedelta(days=n.expire_days) > now)
    ]

    unread_notifications = [
        n for n in valid_notifications if n.id not in seen_notifications
    ]

    return JsonResponse({
        'count': len(unread_notifications)
    })





from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone

from .models import Notification, NotificationSeen, NotificationGroup

@login_required
def read_notifications_list(request):
    user = request.user

    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        hidden=False
    )

    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False) |
        Q(group__needs_approval=True, status=Notification.STATUS_APPROVED)
    )

    seen_notifications = NotificationSeen.objects.filter(
        user=user
    ).values_list('notification_id', flat=True)

    now = timezone.now()

    valid_notifications = [
        n for n in notifications
        if (n.expire_days is None) or (n.created_at + timedelta(days=n.expire_days) > now)
    ]

    read_notifications = [
        n for n in valid_notifications if n.id in seen_notifications
    ]

    read_notifications.sort(key=lambda x: x.created_at, reverse=True)

    return render(request, 'notification/read_notifications_list.html', {
        'notifications': read_notifications
    })





# notification/views.py

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Notification, NotificationGroup
from django.contrib import messages

@method_decorator(login_required, name='dispatch')
class PendingNotificationsListView(ListView):
    model = Notification
    template_name = 'notification/pending_notifications_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        user = self.request.user
        managed_groups = NotificationGroup.objects.filter(managers=user)
        return Notification.objects.filter(
            group__in=managed_groups,
            status=Notification.STATUS_PENDING
        )



# notification/views.py

from django import forms

class NotificationApprovalForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'expire_days', 'status']

@method_decorator(login_required, name='dispatch')
class NotificationApprovalUpdateView(UpdateView):
    model = Notification
    form_class = NotificationApprovalForm
    template_name = 'notification/notification_approval_form.html'
    success_url = reverse_lazy('notification:pending_notifications_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.group.managers.filter(id=request.user.id).exists():
            messages.error(request, "شما اجازه دسترسی به این پیام را ندارید.")
            return redirect('notification:pending_notifications_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "پیام با موفقیت بروزرسانی شد.")
        return super().form_valid(form)








from django.shortcuts import render
from notification.models import NotificationCoupon, NotificationCouponPurchase
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from notification.models import NotificationCoupon, NotificationCouponPurchase

@login_required
def coupon_list(request):
    user = request.user

    coupons = NotificationCoupon.objects.filter(user=user)
    purchases = NotificationCouponPurchase.objects.filter(user=user).order_by('-created_at')

    # جمع تعداد خریداری شده و استفاده شده (در کل)
    total_purchased = coupons.aggregate(total=models.Sum('quantity_purchased'))['total'] or 0
    total_used = coupons.aggregate(total=models.Sum('quantity_used'))['total'] or 0

    context = {
        'coupons': coupons,
        'purchases': purchases,
        'total_purchased': total_purchased,
        'total_used': total_used,
    }
    return render(request, 'notification/coupon_list.html', context)






from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, NotificationSeen

from django.views.decorators.http import require_POST





from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

@require_POST
@login_required
def mark_read(request):
    try:
        data = json.loads(request.body)
        ids = data.get('notification_ids', [])
        if not ids:
            return JsonResponse({'status': 'error', 'message': 'No notification_ids provided'}, status=400)

        notifs = Notification.objects.filter(id__in=ids)
        for notif in notifs:
            NotificationSeen.objects.get_or_create(user=request.user, notification=notif)

        return JsonResponse({'status': 'ok', 'marked_ids': ids})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)









from django.http import JsonResponse
from django.contrib.auth.decorators import login_required




from django.http import JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, IntegerField
from django.contrib.auth.decorators import login_required
from .models import NotificationGroup, NotificationCoupon









from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, IntegerField
from django.http import JsonResponse

from .models import NotificationGroup, NotificationCoupon




from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, IntegerField
from django.http import JsonResponse

from .models import NotificationGroup, NotificationCoupon


@login_required
def user_coupons_for_group(request, group_id):
    print(f"DEBUG: user_coupons_for_group called with group_id={group_id}")

    user = request.user
    try:
        group = NotificationGroup.objects.get(id=group_id)
    except NotificationGroup.DoesNotExist:
        return JsonResponse({'error': 'گروه یافت نشد'}, status=404)

    user_coupons = NotificationCoupon.objects.filter(user=user, group=group)
    total_remaining = user_coupons.aggregate(
        total_remaining=Sum(
            ExpressionWrapper(
                F('quantity_purchased') - F('quantity_used'),
                output_field=IntegerField()
            )
        )
    )['total_remaining'] or 0

    return JsonResponse({
        'default_expire_days': group.default_expire_days,
        'send_cost': group.send_cost,
        'available_coupons': total_remaining,
        'group_title': group.title,
    })






















@login_required
def delete_user_coupons_for_group(request, group_id):
    user = request.user
    try:
        group = NotificationGroup.objects.get(id=group_id)
    except NotificationGroup.DoesNotExist:
        return JsonResponse({'error': 'گروه یافت نشد'}, status=404)

    user_coupons = NotificationCoupon.objects.filter(user=user, group=group)
    total_remaining = user_coupons.aggregate(
        total_remaining=Sum(
            ExpressionWrapper(F('quantity_purchased') - F('quantity_used'), output_field=IntegerField())
        )
    )['total_remaining'] or 0

    return JsonResponse({
        'send_cost': group.send_cost,
        'available_coupons': total_remaining,
        'group_title': group.title,
    })





