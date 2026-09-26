from django.conf import settings
from django.db import models

from store.models import Product


class Cart(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='کاربر',
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
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'

    def __str__(self):
        return f'سبد خرید {self.user.phone}'

    @property
    def total_items(self):
        return sum(
            item.quantity
            for item in self.items.all()
        )

    @property
    def items_total(self):
        return sum(
            item.total_price
            for item in self.items.all()
        )


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد خرید',
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='محصول',
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد',
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
        verbose_name = 'قلم سبد خرید'
        verbose_name_plural = 'اقلام سبد خرید'

        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_product',
            ),
        ]

    def __str__(self):
        return f'{self.product.title} × {self.quantity}'

    @property
    def unit_price(self):
        return self.product.final_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Coupon(models.Model):

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد تخفیف',
    )

    discount_percent = models.PositiveSmallIntegerField(
        verbose_name='درصد تخفیف',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ انقضا',
    )

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'

    def __str__(self):
        return self.code


class Order(models.Model):

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SHIPPING = 'shipping'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار پرداخت'),
        (STATUS_PAID, 'پرداخت شده'),
        (STATUS_SHIPPING, 'در حال ارسال'),
        (STATUS_DELIVERED, 'تحویل شده'),
        (STATUS_CANCELLED, 'لغو شده'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='کاربر',
    )

    number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='شماره سفارش',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='وضعیت',
    )

    total_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ کل',
    )

    discount_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ تخفیف',
    )

    final_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ نهایی',
    )

    recipient_name = models.CharField(
        max_length=150,
        verbose_name='نام گیرنده',
    )

    phone = models.CharField(
        max_length=11,
        verbose_name='شماره تماس',
    )

    province = models.CharField(
        max_length=100,
        verbose_name='استان',
    )

    city = models.CharField(
        max_length=100,
        verbose_name='شهر',
    )

    address = models.TextField(
        verbose_name='آدرس',
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='کد پستی',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']

    def __str__(self):
        return self.number

    @property
    def status_label(self):
        return self.get_status_display()


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش',
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='محصول',
    )

    product_title = models.CharField(
        max_length=250,
        verbose_name='عنوان محصول',
    )

    sku = models.CharField(
        max_length=100,
        verbose_name='کد محصول',
    )

    unit_price = models.PositiveBigIntegerField(
        verbose_name='قیمت واحد',
    )

    quantity = models.PositiveIntegerField(
        verbose_name='تعداد',
    )

    total_price = models.PositiveBigIntegerField(
        verbose_name='قیمت کل',
    )

    class Meta:
        verbose_name = 'قلم سفارش'
        verbose_name_plural = 'اقلام سفارش'

    def __str__(self):
        return f'{self.product_title} × {self.quantity}'