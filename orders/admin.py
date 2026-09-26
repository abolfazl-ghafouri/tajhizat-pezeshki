from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Coupon,
    Order,
    OrderItem,
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'total_items',
        'items_total',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'user__phone',
        'user__full_name',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    inlines = [
        CartItemInline,
    ]

    ordering = (
        '-updated_at',
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        'code',
        'discount_percent',
        'is_active',
        'expires_at',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'code',
    )

    list_editable = (
        'discount_percent',
        'is_active',
    )

    ordering = (
        '-id',
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        'product',
        'product_title',
        'sku',
        'unit_price',
        'quantity',
        'total_price',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'number',
        'user',
        'status',
        'final_amount',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'number',
        'user__phone',
        'user__full_name',
        'recipient_name',
        'phone',
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )

    fieldsets = (
        (
            'اطلاعات سفارش',
            {
                'fields': (
                    'number',
                    'user',
                    'status',
                ),
            },
        ),
        (
            'مبالغ',
            {
                'fields': (
                    'total_amount',
                    'discount_amount',
                    'final_amount',
                ),
            },
        ),
        (
            'اطلاعات گیرنده',
            {
                'fields': (
                    'recipient_name',
                    'phone',
                    'province',
                    'city',
                    'address',
                    'postal_code',
                ),
            },
        ),
        (
            'تاریخ',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
            },
        ),
    )

    inlines = [
        OrderItemInline,
    ]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        'cart',
        'product',
        'quantity',
        'unit_price',
        'total_price',
    )

    search_fields = (
        'cart__user__phone',
        'product__title',
        'product__sku',
    )

    ordering = (
        '-updated_at',
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'product_title',
        'sku',
        'quantity',
        'unit_price',
        'total_price',
    )

    search_fields = (
        'order__number',
        'product_title',
        'sku',
    )

    readonly_fields = (
        'product',
        'product_title',
        'sku',
        'unit_price',
        'quantity',
        'total_price',
    )