from django.contrib import admin

from .models import (
    Brand,
    Category,
    Favorite,
    Product,
    ProductFAQ,
    ProductImage,
    ProductReview,
    ProductSpecification,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',),
    }

    ordering = (
        'name',
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',),
    }

    ordering = (
        'name',
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductFAQInline(admin.TabularInline):
    model = ProductFAQ
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'category',
        'brand',
        'price',
        'discount_price',
        'stock',
        'is_featured',
        'is_active',
        'created_at',
    )

    list_filter = (
        'category',
        'brand',
        'is_featured',
        'is_active',
    )

    search_fields = (
        'title',
        'sku',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('title',),
    }

    ordering = (
        '-created_at',
    )

    list_editable = (
        'price',
        'discount_price',
        'stock',
        'is_featured',
        'is_active',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            'اطلاعات اصلی',
            {
                'fields': (
                    'title',
                    'slug',
                    'sku',
                    'category',
                    'brand',
                ),
            },
        ),
        (
            'توضیحات',
            {
                'fields': (
                    'short_description',
                    'description',
                ),
            },
        ),
        (
            'قیمت و موجودی',
            {
                'fields': (
                    'price',
                    'discount_price',
                    'stock',
                    'warranty_text',
                ),
            },
        ),
        (
            'نمایش',
            {
                'fields': (
                    'badge',
                    'main_image',
                    'is_featured',
                    'is_active',
                ),
            },
        ),
        (
            'زمان',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
            },
        ),
    )

    inlines = [
        ProductImageInline,
        ProductSpecificationInline,
        ProductFAQInline,
    ]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'user',
        'rating',
        'is_approved',
        'created_at',
    )

    list_filter = (
        'rating',
        'is_approved',
        'created_at',
    )

    search_fields = (
        'product__title',
        'user__phone',
        'body',
    )

    list_editable = (
        'is_approved',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'product',
        'created_at',
    )

    search_fields = (
        'user__phone',
        'product__title',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'order',
        'alt_text',
    )

    search_fields = (
        'product__title',
        'alt_text',
    )

    ordering = (
        'product',
        'order',
    )


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'name',
        'value',
        'order',
    )

    search_fields = (
        'product__title',
        'name',
        'value',
    )

    ordering = (
        'product',
        'order',
    )


@admin.register(ProductFAQ)
class ProductFAQAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'question',
        'is_active',
        'order',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'product__title',
        'question',
        'answer',
    )

    list_editable = (
        'is_active',
        'order',
    )

    ordering = (
        'product',
        'order',
    )