# news/api_views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils import timezone
from .models import News, Category
from .serializers import (
    CategorySerializer,
    NewsSerializer,
    NewsCreateSerializer
)

class CategoryListAPI(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.allowed_categories.all()


class NewsListAPI(generics.ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        qs = News.objects.all().order_by('-created_at')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs





# news/api_views.py
class NewsCreateAPI(generics.CreateAPIView):
    serializer_class = NewsCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        category = serializer.validated_data['category']
        daily_limit = category.daily_limit
        today = timezone.now().date()

        if daily_limit > 0:
            count_today = News.objects.filter(
                category=category,
                created_at__date=today
            ).count()
            if count_today >= daily_limit:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    "category": f'سقف روزانه دسته‌بندی "{category.name}" برای امروز پر شده است.'
                })

        serializer.save(author=self.request.user)









from rest_framework.exceptions import PermissionDenied





# news/api_views.py
from rest_framework import generics, permissions
from .models import News
from .serializers import NewsSerializer, NewsUpdateSerializer

class NewsUpdateAPIView(generics.UpdateAPIView):
    queryset = News.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NewsUpdateSerializer

    def get_queryset(self):
        # فقط خبرهایی که خود کاربر نوشته رو برگردون
        return News.objects.filter(author=self.request.user)

    def get_serializer_class(self):
        # بعد از ویرایش خروجی رو کامل نشون بده
        if self.request.method in ['PATCH', 'PUT']:
            return NewsUpdateSerializer
        return NewsSerializer







# news/api_views.py
class NewsDeleteAPIView(generics.DestroyAPIView):
    queryset = News.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("شما اجازه حذف این خبر را ندارید.")

        from django.utils import timezone
        diff = timezone.now() - instance.created_at
        if diff.total_seconds() > 2 * 60:  # بیشتر از ۲ دقیقه
            raise PermissionDenied("امکان حذف بعد از ۲ دقیقه وجود ندارد.")

        instance.delete()




from rest_framework.decorators import api_view
from django.utils.timezone import now

@api_view(['GET'])
def check_daily_limit_apiview(request):
    category_id = request.GET.get("category_id")

    if not category_id:
        return Response({
            "ok": False,
            "message": "هیچ شناسه‌ای ارسال نشده.",
            "can_submit": False,
        })

    try:
        category_id = int(category_id)
    except ValueError:
        return Response({
            "ok": False,
            "message": "شناسه دسته‌بندی معتبر نیست.",
            "can_submit": False,
        })

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({
            "ok": False,
            "message": "دسته‌بندی پیدا نشد.",
            "can_submit": False,
        })

    today = now().date()
    count_today = News.objects.filter(
        category=category,
        created_at__date=today
    ).count()

    can_submit = count_today < category.daily_limit

    return Response({
        "ok": can_submit,
        "message": (
            f"می‌توانید خبر ارسال کنید."
            if can_submit
            else f"سقف مجاز ارسال خبر در دسته‌بندی '{category.name}' برای امروز پر شده است."
        ),
        "daily_limit": category.daily_limit,
        "count_today": count_today,
        "can_submit": can_submit,
    })



