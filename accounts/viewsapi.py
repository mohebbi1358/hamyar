
#api
from rest_framework import status
import re
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.response import Response
from rest_framework.views import APIView
from main.views import MeliPayamakAPI
from accounts.models import User, Persona
import re
from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model, login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken











SMS_CODE_STORAGE = {}

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



User = get_user_model()

class LoginAPIView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        action = request.data.get("action")

        if not phone:
            return Response({"error": "شماره موبایل الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^09\d{9}$', phone):
            return Response({"error": "فرمت شماره موبایل معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'login_password':
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return Response({"error": "نام کاربری یا رمز عبور اشتباه است."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response({"error": "نام کاربری یا رمز عبور اشتباه است."}, status=status.HTTP_400_BAD_REQUEST)

            login(request, user)

            # ✅ ایجاد توکن JWT برای Flutter
            refresh = RefreshToken.for_user(user)

            return Response({
                "detail": "با موفقیت وارد شدید",
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_profile_completed": user.is_profile_completed,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        elif action == 'send_code':
            now = timezone.now()
            if phone in SMS_CODE_STORAGE:
                last_sent = SMS_CODE_STORAGE[phone]['time']
                if now - last_sent < timedelta(minutes=2):
                    return Response({"error": "هر دو دقیقه فقط یک‌بار می‌توان درخواست داد."},
                                    status=status.HTTP_400_BAD_REQUEST)

            code = get_random_string(length=4, allowed_chars='1234567890')
            SMS_CODE_STORAGE[phone] = {'code': code, 'time': now}

            api = MeliPayamakAPI(
                username=settings.MELI_PAYAMAK_USERNAME,
                password=settings.MELI_PAYAMAK_PASSWORD,
                sender_number=settings.MELI_PAYAMAK_SENDER
            )

            sms_text = f"کد ورود شما: {code}"
            result = api.send_sms(phone, sms_text)

            result_code = 0
            if result:
                match = re.search(r'>(\d+)<', result)
                if match:
                    result_code = int(match.group(1))

            if result_code <= 0:
                error_msg = MELI_PAYAMAK_ERRORS.get(result_code, 'خطا در ارسال پیامک. لطفاً بعداً تلاش کنید.')
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "کد با موفقیت ارسال شد."})

        return Response({"error": "نوع درخواست نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)









from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.contrib.auth import get_user_model

class VerifyCodeAPIView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")

        if not phone or not code:
            return Response({"error": "شماره موبایل و کد الزامی هستند."}, status=400)

        stored = SMS_CODE_STORAGE.get(phone)
        if not stored:
            return Response({"error": "کدی برای این شماره ارسال نشده است."}, status=400)

        if timezone.now() - stored['time'] > timedelta(minutes=2):
            del SMS_CODE_STORAGE[phone]
            return Response({"error": "کد منقضی شده است."}, status=400)

        if stored['code'] != code:
            return Response({"error": "کد اشتباه است."}, status=400)

        User = get_user_model()
        user, created = User.objects.get_or_create(phone=phone)
        login(request, user)

        # ساخت توکن JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            "detail": "ورود با موفقیت انجام شد.",
            "user": {
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_profile_completed": user.is_profile_completed,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })










from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication




class CompleteProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        if not user:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'gender': user.gender or '',
            'phone': user.phone,
        })

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        if not user:
            return Response({'detail': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        gender = data.get('gender')

        if not all([first_name, last_name, password, gender]):
            return Response({'detail': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response({
            'detail': 'Profile completed successfully',
            'user': {
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)




# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from news.models import Category
from news.serializers import CategorySerializer  # فرض بر این است که دارید این سریالایزر را دارید

class UserAllowedCategoriesView(APIView):
    """
    ویوی API برای گرفتن دسته‌بندی‌های مجاز کاربر لاگین‌شده
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        categories = user.allowed_categories.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
