from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(
        self,
        phone,
        full_name='',
        password=None,
        **extra_fields
    ):
        if not phone:
            raise ValueError('شماره موبایل الزامی است.')

        user = self.model(
            phone=phone,
            full_name=full_name,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        phone,
        full_name='',
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(
            phone=phone,
            full_name=full_name,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField(
        max_length=11,
        unique=True,
    )

    full_name = models.CharField(
        max_length=150,
    )

    email = models.EmailField(
        blank=True,
    )

    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name else ''

    @property
    def last_name(self):
        parts = self.full_name.split()

        if len(parts) > 1:
            return ' '.join(parts[1:])

        return ''

    @property
    def initials(self):
        parts = self.full_name.split()

        if len(parts) >= 2:
            return parts[0][0] + parts[1][0]

        if parts:
            return parts[0][0]

        return ''

    def __str__(self):
        return self.phone


class OTPCode(models.Model):

    LOGIN = 'login'
    REGISTER = 'register'

    PURPOSE_CHOICES = [
        (LOGIN, 'ورود'),
        (REGISTER, 'ثبت نام'),
    ]

    phone = models.CharField(
        max_length=11,
    )

    code = models.CharField(
        max_length=6,
    )

    purpose = models.CharField(
        max_length=10,
        choices=PURPOSE_CHOICES,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f'{self.phone} - {self.code}'


class Address(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
    )

    title = models.CharField(
        max_length=100,
        default='آدرس اصلی',
    )

    recipient_name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=11,
    )

    province = models.CharField(
        max_length=100,
    )

    city = models.CharField(
        max_length=100,
    )

    address = models.TextField()

    postal_code = models.CharField(
        max_length=10,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def full_text(self):
        return (
            f'{self.province}، {self.city}، '
            f'{self.address}'
        )

    def __str__(self):
        return f'{self.user.phone} - {self.city}'