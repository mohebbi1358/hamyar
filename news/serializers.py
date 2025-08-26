# news/serializers.py
from django.utils import timezone
from rest_framework import serializers
from .models import News, Category, NewsImage, NewsLink

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'daily_limit']

class NewsLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLink
        fields = ['title', 'url']

class NewsImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewsImage
        fields = ['image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None









class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    links = NewsLinkSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    is_owner = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'category', 'category_name',
            'summary', 'body', 'main_image', 'images', 'links',
            'author_id', 'author_name', 'is_owner', 'created_at'
        ]

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated and obj.author == request.user

    def get_main_image(self, obj):
        request = self.context.get('request')
        if obj.main_image and hasattr(obj.main_image, 'url'):
            return request.build_absolute_uri(obj.main_image.url) if request else obj.main_image.url
        return None














from django.utils import timezone
from rest_framework import serializers
from .models import News, NewsImage, NewsLink

class NewsCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    links = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True,
        required=False
    )

    class Meta:
        model = News
        fields = ['title', 'category', 'summary', 'body', 'main_image', 'images', 'links']

    def validate_category(self, value):
        user = self.context['request'].user

        # چک اینکه کاربر مجاز به ارسال خبر در این دسته هست یا نه
        if value not in user.allowed_categories.all():
            raise serializers.ValidationError("شما مجاز به ارسال خبر در این دسته‌بندی نیستید.")

        # محدودیت روزانه
        today = timezone.now().date()
        count_today = News.objects.filter(category=value, created_at__date=today).count()

        if count_today >= value.daily_limit:
            raise serializers.ValidationError(
                f"سقف مجاز ارسال خبر در دسته‌بندی '{value.name}' برای امروز پر شده است."
            )

        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        links_data = validated_data.pop('links', [])

        news = News.objects.create(**validated_data)

        # ذخیره تصاویر
        for img in images_data:
            NewsImage.objects.create(news=news, image=img)

        # ذخیره لینک‌ها فقط اگر داده‌ای وجود داشته باشد
        for link in links_data or []:
            if 'title' in link and 'url' in link:
                NewsLink.objects.create(news=news, **link)

        return news










# news/serializers.py
class NewsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['summary', 'body']

    def validate(self, data):
        instance = self.instance
        if instance:
            diff = timezone.now() - instance.created_at
            if diff.total_seconds() > 2 * 60 * 60:
                raise serializers.ValidationError("امکان ویرایش بعد از ۲ ساعت وجود ندارد.")
        return data


