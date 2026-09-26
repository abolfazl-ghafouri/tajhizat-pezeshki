from django.db import models


class SiteSettings(models.Model):

    site_name = models.CharField(
        max_length=150,
        default='AZRYYAZDAN',
        verbose_name='نام سایت',
    )

    slogan = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='شعار',
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='تلفن',
    )

    email = models.EmailField(
        blank=True,
        verbose_name='ایمیل',
    )

    address = models.TextField(
        blank=True,
        verbose_name='آدرس',
    )

    working_hours = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='ساعات کاری',
    )

    about_text = models.TextField(
        blank=True,
        verbose_name='متن درباره ما',
    )

    logo = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name='لوگو',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self):
        return self.site_name

    @property
    def brand_name(self):
        return self.site_name

    @property
    def phone_display(self):
        return self.phone


class ServiceFeature(models.Model):

    icon = models.CharField(
        max_length=100,
        verbose_name='کلاس آیکون',
    )

    title = models.CharField(
        max_length=150,
        verbose_name='عنوان',
    )

    description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='توضیحات',
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    class Meta:
        verbose_name = 'ویژگی خدمات'
        verbose_name_plural = 'ویژگی های خدمات'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class CompanyStat(models.Model):

    icon = models.CharField(
        max_length=100,
        verbose_name='کلاس آیکون',
    )

    value = models.CharField(
        max_length=50,
        verbose_name='مقدار',
    )

    label = models.CharField(
        max_length=150,
        verbose_name='عنوان',
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    class Meta:
        verbose_name = 'آمار شرکت'
        verbose_name_plural = 'آمار شرکت'
        ordering = ['order', 'id']

    def __str__(self):
        return self.label


class TeamMember(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name='نام',
    )

    email = models.EmailField(
        blank=True,
        verbose_name='ایمیل',
    )

    role = models.CharField(
        max_length=150,
        verbose_name='سمت',
    )

    image = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
        verbose_name='تصویر',
    )

    bio = models.TextField(
        blank=True,
        verbose_name='درباره',
    )

    instagram_url = models.URLField(
        blank=True,
        verbose_name='Instagram',
    )

    linkedin_url = models.URLField(
        blank=True,
        verbose_name='LinkedIn',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب',
    )

    class Meta:
        verbose_name = 'عضو تیم'
        verbose_name_plural = 'اعضای تیم'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url

        return ''


class FAQ(models.Model):

    question = models.CharField(
        max_length=300,
        verbose_name='سوال',
    )

    answer = models.TextField(
        verbose_name='پاسخ',
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question


class NewsletterSubscriber(models.Model):

    email = models.EmailField(
        unique=True,
        verbose_name='ایمیل',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ عضویت',
    )

    class Meta:
        verbose_name = 'عضو خبرنامه'
        verbose_name_plural = 'اعضای خبرنامه'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email