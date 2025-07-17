from .forms import NotificationCreateHidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F, Sum, ExpressionWrapper, IntegerField, Q
from django.core.exceptions import ValidationError

from .models import (
    NotificationGroup, NotificationCoupon, Notification, Eternals, News
)
from .forms import NotificationCreateForm, BuyCouponForm

from wallet.models import Wallet, WalletTransaction
from donation.models import DonationCause, Donation
from notification.services import buy_notification_coupons, confirm_notification_coupon_purchase


from django.http import HttpRequest








from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from .models import NotificationGroup, NotificationCoupon, Eternals, News
from .forms import NotificationCreateForm





@login_required
def create_notification(request):
    user = request.user

    groups = NotificationGroup.objects.filter(
        Q(is_public=True) | Q(allowed_senders=user),
        hidden=False
    ).distinct()

    if request.method == 'POST':
        form = NotificationCreateForm(request.POST)
        form.fields['group'].queryset = groups

        if form.is_valid():
            notif = form.save(commit=False)
            notif.created_by = user

            if notif.group not in groups:
                form.add_error('group', "شما اجازه ارسال پیام در این گروه را ندارید.")
            else:
                # کوپن فقط اگر گروه پولی بود چک کن
                if notif.group.send_cost > 0:
                    user_coupon = NotificationCoupon.objects.filter(
                        user=user,
                        group=notif.group,
                        quantity_purchased__gt=F('quantity_used') + F('quantity_reserved')
                    ).order_by('id').first()

                    if not user_coupon:
                        form.add_error(None, "برای ارسال پیام در این گروه باید کوپن ارسال پیام تهیه نمایید.")
                    else:
                        user_coupon.quantity_reserved += 1
                        user_coupon.save()
                        notif.coupon_reserved_id = user_coupon.id

            # فیلدهای optional
            eternal_id = request.POST.get('eternal')
            news_id = request.POST.get('news')

            try:
                notif.eternal = Eternals.objects.get(id=eternal_id) if eternal_id else None
            except Eternals.DoesNotExist:
                notif.eternal = None

            try:
                notif.news = News.objects.get(id=news_id) if news_id else None
            except News.DoesNotExist:
                notif.news = None

            # اعتبارسنجی مدل
            try:
                notif.clean()
            except ValidationError as e:
                form.add_error(None, e)

            if not form.errors:
                # ✅ تعیین وضعیت پیام
                if notif.group.needs_approval:
                    notif.status = 'PENDING'
                else:
                    notif.status = 'SENT'

                notif.save()
                messages.success(request, "پیام با موفقیت ثبت شد.")
                return redirect('notification:unread_notifications_list')

        # اگر فرم معتبر نبود یا ارور داشت، دوباره رندر کن

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

    form.fields['group'].queryset = groups

    return render(request, 'notification/create_notification.html', {'form': form})
















@login_required
def buy_coupon(request):
    print(f"VIEW CALLED: {__name__}.buy_coupon")
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
                # پرداخت آنلاین یا سایر روش‌ها
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
    print(f"VIEW CALLED: {__name__}.delete_assign_coupons_to_user")
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


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

from .models import (
    Notification, NotificationSeen, NotificationGroup, NotificationGroupMembership
)
from .forms import NotificationSettingsForm, NotificationGroupForm
from notification.services import confirm_notification_coupon_purchase
from donation.models import Donation, DonationCause
from wallet.models import Wallet, WalletTransaction
from eternals.models import Eternals
from news.models import News


@login_required
def notifications_list(request):
    print(f"VIEW CALLED: {__name__}.notifications_list")
    user = request.user
    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        hidden=False
    )
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
    print(f"VIEW CALLED: {__name__}.notification_detail")
    notif = get_object_or_404(Notification, pk=pk)

    if notif.group.hidden:
        return redirect('notification:notifications_list')

    NotificationSeen.objects.get_or_create(
        user=request.user,
        notification=notif
    )

    return render(request, 'notification/notification_detail.html', {
        'notification': notif
    })


@login_required
def notification_settings(request):
    print(f"VIEW CALLED: {__name__}.notification_settings")
    user = request.user
    all_groups = NotificationGroup.objects.filter(is_mandatory=False, hidden=False)
    user_groups = NotificationGroup.objects.filter(memberships__user=user)

    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST)
        if form.is_valid():
            selected_groups = form.cleaned_data['groups']
            NotificationGroupMembership.objects.filter(user=user).delete()
            for group in selected_groups:
                NotificationGroupMembership.objects.create(user=user, group=group)
            return redirect('notification:notification_settings')
    else:
        form = NotificationSettingsForm(initial={'groups': user_groups})

    return render(request, 'notification/notification_settings.html', {'form': form})


# --- Superuser Views for NotificationGroup ---

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def notification_group_list(request):
    print(f"VIEW CALLED: {__name__}.notification_group_list")
    groups = NotificationGroup.objects.all()
    return render(request, 'notification/group_list.html', {'groups': groups})








# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .forms import NotificationGroupForm
from .models import NotificationGroup

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@superuser_required
def notification_group_create(request):
    if request.method == 'POST':
        form = NotificationGroupForm(request.POST)
        if form.is_valid():
            form.save()
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
    print(f"VIEW CALLED: {__name__}.notification_group_delete")
    group = get_object_or_404(NotificationGroup, pk=pk)
    group.delete()
    return redirect('notification:notification_group_list')





@login_required
def unread_notifications_list(request):
    print(f"VIEW CALLED: {__name__}.unread_notifications_list")
    user = request.user
    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        #hidden=False
    )
    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False, status=Notification.STATUS_SENT) |
        Q(group__needs_approval=True, status=Notification.STATUS_APPROVED)
    )
    seen_notifications = NotificationSeen.objects.filter(user=user).values_list('notification_id', flat=True)
    now = timezone.now()

    valid_notifications = [
        n for n in notifications
        if (n.expire_days is None) or (n.created_at + timedelta(days=n.expire_days) > now)
    ]
    unread_notifications = [n for n in valid_notifications if n.id not in seen_notifications]
    unread_notifications.sort(key=lambda x: x.created_at, reverse=True)
    print("USER:", user.id, user.get_full_name())
    print("GROUPS QUERY:", groups.values_list('id', 'title', 'hidden', 'needs_approval', 'is_public'))
    print("ALL NOTIFS:", Notification.objects.all().values_list('id', 'group_id', 'status'))
    print("NOTIFICATIONS:", notifications.values_list('id', 'group_id', 'status'))

    return render(request, 'notification/unread_notifications_list.html', {
        'notifications': unread_notifications
    })


@login_required
def unread_notifications_count(request):
    print(f"VIEW CALLED: {__name__}.unread_notifications_count")
    user = request.user
    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        #hidden=False
    )
    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False, status=Notification.STATUS_SENT) |
        Q(group__needs_approval=True, status=Notification.STATUS_APPROVED)
    )
    seen_notifications = NotificationSeen.objects.filter(user=user).values_list('notification_id', flat=True)
    now = timezone.now()

    valid_notifications = [
        n for n in notifications
        if (n.expire_days is None) or (n.created_at + timedelta(days=n.expire_days) > now)
    ]
    unread_notifications = [n for n in valid_notifications if n.id not in seen_notifications]

    return JsonResponse({'count': len(unread_notifications)})


# --- AJAX Search ---

@login_required
def delete_ajax_search_eternals(request):
    print(f"VIEW CALLED: {__name__}.ajax_search_eternals")
    q = request.GET.get('q', '').strip()
    eternals = Eternals.objects.all()

    if q:
        for word in q.split():
            eternals = eternals.filter(
                Q(first_name__icontains=word) | Q(last_name__icontains=word)
            )

    eternals = eternals.order_by('-created_at')[:20]

    data = {
        "results": [
            {"id": e.id, "text": f"{e.first_name} {e.last_name}"}
            for e in eternals
        ]
    }
    return JsonResponse(data)


@require_GET
def delete_ajax_search_news(request):
    print(f"VIEW CALLED: {__name__}.ajax_search_news")
    q = request.GET.get('q', '').strip()
    results = []

    if q:
        qs = News.objects.filter(title__icontains=q).order_by('-created_at')[:20]
        results = [{'id': news.id, 'text': news.title} for news in qs]

    return JsonResponse({'results': results})


# --- NotificationGroup Detail API ---

from django.views import View

class NotificationGroupDetailView(View):
    print(f"VIEW CALLED: {__name__}.NotificationGroupDetailView")
    def get(self, request, pk):
        try:
            group = NotificationGroup.objects.get(pk=pk)
            return JsonResponse({'default_expire_days': group.default_expire_days})
        except NotificationGroup.DoesNotExist:
            return JsonResponse({'default_expire_days': 30})


# --- Payment Callback ---

@csrf_exempt
def delete_payment_callback(request, donation_id):
    print(f"VIEW CALLED: {__name__}.delete_payment_callback")
    print("notification \ CALLBACK CALLED")
    print("status:", request.GET.get('status'))
    print("ref_id:", request.GET.get('ref_id'))

    donation = get_object_or_404(Donation, id=donation_id)
    status = request.GET.get('status', 'FAILED')
    ref_id = request.GET.get('ref_id', '')

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




from datetime import timedelta
import json

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, ExpressionWrapper, IntegerField
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, UpdateView

from .models import (
    Notification, NotificationSeen, NotificationGroup,
    NotificationCoupon, NotificationCouponPurchase
)


# ------------------------------------
# 1. نمایش نوتیفیکیشن‌های خوانده شده (کاربر)
# ------------------------------------
@login_required
def read_notifications_list(request):
    print(f"VIEW CALLED: {__name__}.read_notifications_list")
    user = request.user

    groups = NotificationGroup.objects.filter(
        memberships__user=user,
        #hidden=False
    )
    notifications = Notification.objects.filter(
        group__in=groups
    ).filter(
        Q(group__needs_approval=False, status=Notification.STATUS_SENT) |
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


# ------------------------------------
# 2. نمایش نوتیفیکیشن‌های منتظر تایید (مدیران گروه‌ها)
# ------------------------------------
@method_decorator(login_required, name='dispatch')
class PendingNotificationsListView(ListView):
    print(f"VIEW CALLED: {__name__}.PendingNotificationsListView")
    model = Notification
    template_name = 'notification/pending_notifications_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        user = self.request.user
        managed_groups = NotificationGroup.objects.filter(managers=user)
        return Notification.objects.filter(
            group__in=managed_groups,
            status=Notification.STATUS_PENDING
        ).order_by('-created_at')


# ------------------------------------
# 3. فرم تایید و بروزرسانی نوتیفیکیشن و ویو مربوطه
# ------------------------------------

class NotificationApprovalForm(forms.ModelForm):
    print(f"VIEW CALLED: {__name__}.NotificationApprovalForm")
    class Meta:
        model = Notification
        fields = ['title', 'description', 'expire_days','eternal','news', 'status']









@method_decorator(login_required, name='dispatch')
class NotificationApprovalUpdateView(UpdateView):
    print(f"VIEW CALLED: {__name__}.NotificationApprovalUpdateView")
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
        notif = form.save(commit=False)

        # وضعیت قبلی پیام
        prev_status = notif.__class__.objects.get(pk=notif.pk).status

        if notif.status == Notification.STATUS_REJECTED:
            # اگر پیام رد شده و کوپن رزرو شده دارد → کوپن را آزاد کن
            if notif.coupon_reserved:
                coupon = notif.coupon_reserved
                if coupon.quantity_reserved > 0:
                    coupon.quantity_reserved -= 1
                    coupon.save()
                notif.coupon_reserved = None

        elif notif.status == Notification.STATUS_APPROVED:
            # اگر پیام تأیید شده و کوپن رزرو شده دارد → کوپن را مصرف کن
            if notif.coupon_reserved:
                coupon = notif.coupon_reserved
                if coupon.quantity_reserved > 0:
                    coupon.quantity_reserved -= 1
                    coupon.quantity_used += 1
                    coupon.save()

        notif.save()

        messages.success(self.request, "پیام با موفقیت بروزرسانی شد.")
        return super().form_valid(form)











from django.db.models import Sum

@login_required
def coupon_list(request):
    print(f"VIEW CALLED: {__name__}.coupon_list")
    user = request.user

    coupons = NotificationCoupon.objects.filter(user=user)
    purchases = NotificationCouponPurchase.objects.filter(user=user).order_by('-created_at')

    total_purchased = coupons.aggregate(total=Sum('quantity_purchased'))['total'] or 0
    total_used = coupons.aggregate(total=Sum('quantity_used'))['total'] or 0
    total_reserved = coupons.aggregate(total=Sum('quantity_reserved'))['total'] or 0

    context = {
        'coupons': coupons,
        'purchases': purchases,
        'total_purchased': total_purchased,
        'total_used': total_used,
        'total_reserved': total_reserved,
    }
    return render(request, 'notification/coupon_list.html', context)





# ------------------------------------
# 5. علامت‌گذاری نوتیفیکیشن‌ها به عنوان خوانده شده (AJAX)
# ------------------------------------
@require_POST
@login_required
def mark_read(request):
    print(f"VIEW CALLED: {__name__}.mark_read")
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




# ------------------------------------
# 7. حذف کوپن‌های کاربر برای یک گروه (AJAX)
# ------------------------------------
@login_required
def delete_user_coupons_for_group(request, group_id):
    print(f"VIEW CALLED: {__name__}.delete_user_coupons_for_group")
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



@login_required
def user_coupons_for_group(request, group_id):
    print(f"VIEW CALLED: {__name__}.user_coupons_for_group")

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




from django.contrib.auth.decorators import user_passes_test

def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='managers').exists()







@login_required
def create_notification_hidden(request):
    if request.method == 'POST':
        form = NotificationCreateHidden(request.POST, user=request.user)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.created_by = request.user

            if not notif.group.hidden:
                form.add_error('group', 'گروه انتخاب شده مخفی نیست.')
                return render(request, 'notification/create_notification_hidden.html', {'form': form})

            if notif.group.send_cost > 0:
                from django.db.models import F
                user_coupon = NotificationCoupon.objects.filter(
                    user=request.user,
                    group=notif.group,
                    quantity_purchased__gt=F('quantity_used') + F('quantity_reserved')
                ).order_by('id').first()
                if not user_coupon:
                    form.add_error(None, "برای ارسال پیام در این گروه باید کوپن ارسال پیام تهیه نمایید.")
                    return render(request, 'notification/create_notification_hidden.html', {'form': form})
                else:
                    user_coupon.quantity_reserved += 1
                    user_coupon.save()
                    notif.coupon_reserved_id = user_coupon.id

            # ✅ این خط را اضافه کن
            if notif.group.needs_approval:
                notif.status = 'PENDING'
            else:
                notif.status = 'SENT'

            notif.save()
            from django.contrib import messages
            messages.success(request, "پیام با موفقیت ثبت شد.")
            return redirect('notification:unread_notifications_list')

    else:
        form = NotificationCreateHidden(user=request.user)

    return render(request, 'notification/create_notification_hidden.html', {'form': form})






