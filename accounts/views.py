import re
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from main.views import MeliPayamakAPI
from .forms import PersonaForm, UserCategoryAccessForm
from .models import Persona, User


# حافظه موقتی برای ذخیره کدهای پیامک
SMS_CODE_STORAGE = {}

# خطاهای ملی پیامک
MELI_PAYAMAK_ERRORS = {
    0: 'نام کاربری یا رمز عبور اشتباه است.',
    2: 'اعتبار کافی نمی‌باشد.',
    3: 'محدودیت در ارسال روزانه.',
    4: 'محدودیت در حجم ارسال.',
    5: 'شماره فرستنده معتبر نمی‌باشد.',
    6: 'سامانه در حال بروزرسانی می‌باشد.',
    7: 'متن حاوی کلمه فیلتر شده می‌باشد.',
    9: 'ارسال از خطوط عمومی از طریق وب‌سرویس امکان‌پذیر نمی‌باشد.',
    10: 'کاربر مورد نظر فعال نمی‌باشد.',
    11: 'پیام ارسال نشده است.',
    12: 'مدارک کاربر کامل نمی‌باشد.',
    14: 'متن حاوی لینک می‌باشد.',
    15: 'ارسال به بیش از 1 شماره بدون درج "لغو11" ممکن نیست.',
    16: 'شماره گیرنده یافت نشد.',
    17: 'متن پیامک خالی است.',
    35: 'شماره در لیست سیاه مخابرات قرار دارد.',
}


# --- API Views ---

class SendSMSCodeView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "Phone is required"}, status=400)

        current_time = timezone.now()

        if phone in SMS_CODE_STORAGE:
            last_sent_time = SMS_CODE_STORAGE[phone]['time']
            if current_time - last_sent_time < timedelta(minutes=2):
                return Response({"error": "You can only request a code every 2 minutes."}, status=400)

        code = get_random_string(length=4, allowed_chars='1234567890')

        SMS_CODE_STORAGE[phone] = {
            'code': code,
            'time': current_time
        }

        api = MeliPayamakAPI(
            username=settings.MELI_PAYAMAK_USERNAME,
            password=settings.MELI_PAYAMAK_PASSWORD,
            sender_number=settings.MELI_PAYAMAK_SENDER
        )
        sms_text = f"کد ورود شما: {code}"
        result = api.send_sms(phone, sms_text)
        
        print("=== MELI PAYAMAK RAW RESPONSE ===")
        print(result)

        return Response({"detail": "Code sent"}, status=200)


class VerifySMSCodeView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")

        if phone not in SMS_CODE_STORAGE:
            return Response({"error": "No code sent for this phone number."}, status=400)

        stored_code_data = SMS_CODE_STORAGE[phone]
        code_sent_time = stored_code_data['time']
        current_time = timezone.now()

        if current_time - code_sent_time > timedelta(minutes=2):
            del SMS_CODE_STORAGE[phone]
            return Response({"error": "The code has expired."}, status=400)

        if stored_code_data['code'] != code:
            return Response({"error": "Invalid code."}, status=400)

        user, created = User.objects.get_or_create(phone=phone)
        return Response({"detail": "Code verified, continue to profile"}, status=200)


# --- Template Views ---

# ذخیره کدها در حافظه



def is_valid_phone(phone):
    return re.fullmatch(r'^09\d{9}$', phone)


def login_view(request):
    if request.method != 'POST':
        return render(request, 'accounts/login.html')

    phone = request.POST.get('phone')
    password = request.POST.get('password')
    action = request.POST.get('action')

    if not phone:
        return render(request, 'accounts/login.html', {'error': 'شماره موبایل الزامی است.'})

    if not is_valid_phone(phone):
        return render(request, 'accounts/login.html', {'error': 'فرمت شماره موبایل نامعتبر است.'})

    User = get_user_model()

    # ورود با رمز
    if action == 'login_password':
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            user = None

        if user and user.check_password(password):
            login(request, user)  # ✅ مورد 4: ورود بعد از تأیید رمز
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': 'شماره یا رمز اشتباه است.'})

    # ارسال کد
    elif action == 'send_code':
        now = timezone.now()

        if phone in SMS_CODE_STORAGE:
            last_sent = SMS_CODE_STORAGE[phone]['time']
            if now - last_sent < timedelta(minutes=2):
                return render(request, 'accounts/login.html', {
                    'error': 'هر دو دقیقه فقط یک‌بار می‌توان درخواست داد.'
                })

        code = get_random_string(length=4, allowed_chars='1234567890')
        SMS_CODE_STORAGE[phone] = {'code': code, 'time': now}

        api = MeliPayamakAPI(
            username=settings.MELI_PAYAMAK_USERNAME,
            password=settings.MELI_PAYAMAK_PASSWORD,
            sender_number=settings.MELI_PAYAMAK_SENDER
        )
        sms_text = f"کد ورود شما: {code}"
        result = api.send_sms(phone, sms_text)

        # ✅ مورد 3: بررسی نتیجه ارسال
        result_code = 0
        if result:
            match = re.search(r'>(-?\d+)<', result)
            if match:
                result_code = int(match.group(1))

        if result_code < 0:
            error_msg = MELI_PAYAMAK_ERRORS.get(result_code, 'خطا در ارسال پیامک. لطفاً بعداً تلاش کنید.')
            return render(request, 'accounts/login.html', {'error': error_msg})

        return redirect(f"{reverse('accounts:verify')}?phone={phone}")

    # درخواست نامعتبر
    return render(request, 'accounts/login.html', {'error': 'درخواست نامعتبر است.'})








def verify_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')

        stored_data = SMS_CODE_STORAGE.get(phone)
        if stored_data and stored_data['code'] == code:
            User = get_user_model()
            user, created = User.objects.get_or_create(phone=phone)
            login(request, user)
            return redirect('accounts:complete_profile')
        else:
            return render(request, 'accounts/verify.html', {
                'error': 'کد وارد شده معتبر نیست.',
                'phone': phone
            })

    phone = request.GET.get('phone')
    return render(request, 'accounts/verify.html', {'phone': phone})


class CompleteProfileView(View):
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        phone = request.GET.get('phone')

        if not user and phone:
            user = User.objects.filter(phone=phone).first()

        if not user:
            return redirect('login')

        return render(request, 'accounts/complete_profile.html', {
            'user': user,
            'gender_choices': User.GENDER_CHOICES
        })

    def post(self, request):
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        gender = request.POST.get('gender')

        user = User.objects.filter(phone=phone).first()
        if not user:
            return redirect('login')

        if not all([first_name, last_name, password, gender]):
            return render(request, 'accounts/complete_profile.html', {
                'error': 'تمام فیلدها الزامی است!',
                'user': user,
                'gender_choices': User.GENDER_CHOICES
            })

        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.set_password(password)
        user.is_profile_completed = True
        user.save()

        full_name = f"{first_name} {last_name}".strip()
        real_persona = user.personas.filter(persona_type=Persona.PersonaType.REAL).first()
        if real_persona:
            real_persona.name = full_name
            real_persona.save()
        else:
            Persona.objects.create(
                user=user,
                name=full_name,
                persona_type=Persona.PersonaType.REAL,
                is_default=True
            )

        login(request, user)
        return redirect('home')


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@user_passes_test(lambda u: u.is_staff)
def assign_categories_to_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserCategoryAccessForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('accounts:user_list')
    else:
        form = UserCategoryAccessForm(instance=user)

    return render(request, 'accounts/assign_categories.html', {'form': form, 'target_user': user})


@staff_member_required
def user_list(request):
    query = request.GET.get('q', '')
    users = User.objects.all()

    if query:
        terms = query.strip().split()
        for term in terms:
            users = users.filter(
                Q(first_name__icontains=term) |
                Q(last_name__icontains=term) |
                Q(phone__icontains=term)
            )

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'query': query,
    })


@staff_member_required
def manage_user_personas(request, user_id):
    user = get_object_or_404(User, id=user_id)
    personas = user.personas.all()

    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            new_persona = form.save(commit=False)
            new_persona.user = user
            new_persona.save()
            return redirect('accounts:manage_personas', user_id=user.id)
    else:
        form = PersonaForm()

    return render(request, 'accounts/manage_personas.html', {
        'target_user': user,
        'personas': personas,
        'form': form,
    })


@staff_member_required
def edit_persona(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id)
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            return redirect('accounts:manage_personas', user_id=persona.user.id)
    else:
        form = PersonaForm(instance=persona)
    return render(request, 'accounts/edit_persona.html', {
        'form': form,
        'persona': persona
    })


@staff_member_required
def delete_persona(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id)
    user_id = persona.user.id
    persona.delete()
    return redirect('accounts:manage_personas', user_id=user_id)


def user_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        users = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(national_code__icontains=q)
        )[:20]
        for user in users:
            results.append({
                'id': user.id,
                'display_name': user.get_display_name() or user.phone,
                'phone': user.phone,
            })
    return JsonResponse(results, safe=False)


def create_superuser_form(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        try:
            user = User.objects.create_superuser(
                phone=phone,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            return HttpResponse(f'کاربر {user.get_display_name()} با موفقیت ساخته شد')
        except Exception as e:
            return HttpResponseServerError(f'خطا: {str(e)}')

    return render(request, 'accounts/create_superuser_form.html')






