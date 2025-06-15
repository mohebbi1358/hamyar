from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'مرد'),
        ('F', 'زن'),
    )

    phone = models.CharField(max_length=11, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    national_code = models.CharField(max_length=10, blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_profile_completed = models.BooleanField(default=False)

    # ارجاع به مدل Category در اپلیکیشن news
    allowed_categories = models.ManyToManyField(
        'news.Category',
        related_name='allowed_users',
        blank=True,
        verbose_name='دسته‌بندی‌های مجاز برای ارسال خبر'
    )

    # جلوگیری از تداخل در related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions_set',
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_gender_prefix(self):
        if self.gender == 'M':
            return 'آقای'
        elif self.gender == 'F':
            return 'خانم'
        return ''

    def get_display_name(self):
        prefix = self.get_gender_prefix()
        full_name = self.get_full_name()
        return f"{prefix} {full_name}".strip()
