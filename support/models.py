from django.conf import settings
from django.db import models

from store.models import Product


class Ticket(models.Model):

    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_ANSWERED = 'answered'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'باز'),
        (STATUS_IN_PROGRESS, 'در حال بررسی'),
        (STATUS_ANSWERED, 'پاسخ داده شده'),
        (STATUS_CLOSED, 'بسته شده'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'کم'),
        (PRIORITY_NORMAL, 'عادی'),
        (PRIORITY_HIGH, 'زیاد'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='کاربر',
    )

    number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='شماره تیکت',
    )

    subject = models.CharField(
        max_length=200,
        verbose_name='موضوع',
    )

    message = models.TextField(
        verbose_name='متن تیکت',
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='دسته بندی',
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL,
        verbose_name='اولویت',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name='وضعیت',
    )

    related_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name='محصول مرتبط',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.number

    @property
    def status_label(self):
        return self.get_status_display()


class ContactMessage(models.Model):

    STATUS_NEW = 'new'
    STATUS_READ = 'read'
    STATUS_REPLIED = 'replied'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'جدید'),
        (STATUS_READ, 'خوانده شده'),
        (STATUS_REPLIED, 'پاسخ داده شده'),
        (STATUS_CLOSED, 'بسته شده'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages',
        verbose_name='کاربر',
    )

    name = models.CharField(
        max_length=150,
        verbose_name='نام',
    )

    email = models.EmailField(
        verbose_name='ایمیل',
    )

    phone = models.CharField(
        max_length=11,
        blank=True,
        verbose_name='شماره موبایل',
    )

    subject = models.CharField(
        max_length=200,
        verbose_name='موضوع',
    )

    message = models.TextField(
        verbose_name='پیام',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='وضعیت',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ارسال',
    )

    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام های تماس'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject


class ConsultationRequest(models.Model):

    STATUS_NEW = 'new'
    STATUS_CONTACTED = 'contacted'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'جدید'),
        (STATUS_CONTACTED, 'تماس گرفته شده'),
        (STATUS_COMPLETED, 'تکمیل شده'),
        (STATUS_CANCELLED, 'لغو شده'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_requests',
        verbose_name='کاربر',
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_requests',
        verbose_name='محصول',
    )

    name = models.CharField(
        max_length=150,
        verbose_name='نام',
    )

    phone = models.CharField(
        max_length=11,
        verbose_name='شماره موبایل',
    )

    email = models.EmailField(
        blank=True,
        verbose_name='ایمیل',
    )

    message = models.TextField(
        blank=True,
        verbose_name='توضیحات',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='وضعیت',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ درخواست',
    )

    class Meta:
        verbose_name = 'درخواست مشاوره'
        verbose_name_plural = 'درخواست های مشاوره'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.phone}'