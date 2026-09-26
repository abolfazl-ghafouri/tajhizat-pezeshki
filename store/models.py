from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='نام دسته بندی',
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='اسلاگ',
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='کلاس آیکون',
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='تصویر',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='نام برند',
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='اسلاگ',
    )

    image = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True,
        verbose_name='لوگو',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name='دسته بندی',
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name='برند',
    )

    title = models.CharField(
        max_length=250,
        verbose_name='عنوان محصول',
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='اسلاگ',
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='کد محصول',
    )

    short_description = models.TextField(
        blank=True,
        verbose_name='توضیح کوتاه',
    )

    description = models.TextField(
        blank=True,
        verbose_name='توضیحات',
    )

    price = models.PositiveBigIntegerField(
        verbose_name='قیمت',
    )

    discount_price = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name='قیمت با تخفیف',
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='موجودی',
    )

    warranty_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='گارانتی',
    )

    badge = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='برچسب',
    )

    main_image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='تصویر اصلی',
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name='محصول ویژه',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
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
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price

        return self.price

    @property
    def discount_percent(self):
        if not self.discount_price or self.discount_price >= self.price:
            return 0

        return round(
            ((self.price - self.discount_price) / self.price) * 100
        )


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='محصول',
    )

    image = models.ImageField(
        upload_to='products/gallery/',
        verbose_name='تصویر',
    )

    alt_text = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='متن جایگزین',
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب',
    )

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصولات'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.product.title} - {self.id}'


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name='محصول',
    )

    name = models.CharField(
        max_length=150,
        verbose_name='عنوان مشخصه',
    )

    value = models.CharField(
        max_length=300,
        verbose_name='مقدار',
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب',
    )

    class Meta:
        verbose_name = 'مشخصه محصول'
        verbose_name_plural = 'مشخصات محصولات'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.product.title} - {self.name}'


class ProductFAQ(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='faqs',
        verbose_name='محصول',
    )

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
        verbose_name = 'سوال متداول محصول'
        verbose_name_plural = 'سوالات متداول محصولات'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question


class ProductReview(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='محصول',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_reviews',
        verbose_name='کاربر',
    )

    rating = models.PositiveSmallIntegerField(
        verbose_name='امتیاز',
    )

    body = models.TextField(
        verbose_name='متن نظر',
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name='تایید شده',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت',
    )

    class Meta:
        verbose_name = 'نظر محصول'
        verbose_name_plural = 'نظرات محصولات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone} - {self.product.title}'

    @property
    def rating_stars(self):
        return '★' * self.rating


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='کاربر',
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='محصول',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    class Meta:
        verbose_name = 'علاقه مندی'
        verbose_name_plural = 'علاقه مندی ها'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_favorite',
            ),
        ]

        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone} - {self.product.title}'