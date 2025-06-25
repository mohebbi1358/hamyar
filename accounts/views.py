from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from .models import User

# حافظه موقتی برای ذخیره کدهای پیامک
SMS_CODE_STORAGE = {}

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

        print(f"[SMS to {phone}] Code: {code}")
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

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        action = request.POST.get('action')

        if not phone:
            return render(request, 'accounts/login.html', {'error': 'شماره موبایل الزامی است'})

        User = get_user_model()

        if action == 'login_password':
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                user = None

            if user and user.check_password(password):
                login(request, user)
                #return redirect('accounts:dashboard') این هم
                return redirect('home')
            else:
                return render(request, 'accounts/login.html', {'error': 'شماره یا رمز اشتباه است'})

        elif action == 'send_code':
            now = timezone.now()
            if phone in SMS_CODE_STORAGE:
                last_sent = SMS_CODE_STORAGE[phone]['time']
                if now - last_sent < timedelta(minutes=2):
                    return render(request, 'accounts/login.html', {'error': 'هر دو دقیقه فقط یک‌بار می‌توان درخواست داد'})

            code = get_random_string(length=4, allowed_chars='1234567890')
            SMS_CODE_STORAGE[phone] = {'code': code, 'time': now}

            print(f"[SMS to {phone}] Code: {code}")
            from django.urls import reverse
            return redirect(f"{reverse('accounts:verify')}?phone={phone}")

    return render(request, 'accounts/login.html')

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

from .models import User  # مطمئن شو که ایمپورت شده

from .models import Persona  # اضافه کن بالای فایل اگر نیست

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
        # ← دریافت اطلاعات فرم
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

        # ← به‌روزرسانی اطلاعات کاربر
        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.set_password(password)
        user.is_profile_completed = True
        user.save()

        # ✅ اضافه کردن شخصیت حقیقی پیش‌فرض (در صورت نبود)
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



from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')




from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect

def logout_view(request):
    logout(request)
    return redirect('home')



from .forms import UserCategoryAccessForm
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def assign_categories_to_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserCategoryAccessForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            #return redirect('accounts:dashboard')  # یا مسیر دلخواه شما
            return redirect('home')  # یا مسیر دلخواه شما
    else:
        form = UserCategoryAccessForm(instance=user)

    return render(request, 'accounts/assign_categories.html', {'form': form, 'target_user': user})



from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Q  # اضافه شود در بالای فایل

@staff_member_required

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


from .forms import PersonaForm

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



