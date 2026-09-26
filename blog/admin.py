from django.contrib import admin

from .models import (
    Article,
    ArticleComment,
    BlogCategory,
    Tag,
)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'icon',
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
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


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):

    list_display = (
        'article',
        'user',
        'is_approved',
        'created_at',
    )

    list_filter = (
        'is_approved',
        'created_at',
    )

    search_fields = (
        'article__title',
        'user__phone',
        'body',
    )

    list_editable = (
        'is_approved',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'author',
        'category',
        'read_time',
        'views',
        'is_featured',
        'is_published',
        'published_at',
    )

    list_filter = (
        'category',
        'is_featured',
        'is_published',
        'tags',
        'published_at',
    )

    search_fields = (
        'title',
        'slug',
        'excerpt',
        'content',
    )

    prepopulated_fields = {
        'slug': ('title',),
    }

    filter_horizontal = (
        'tags',
    )

    list_editable = (
        'is_featured',
        'is_published',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'views',
    )

    ordering = (
        '-published_at',
        '-created_at',
    )

    fieldsets = (
        (
            'اطلاعات اصلی',
            {
                'fields': (
                    'title',
                    'slug',
                    'author',
                    'category',
                    'tags',
                ),
            },
        ),
        (
            'محتوا',
            {
                'fields': (
                    'excerpt',
                    'content',
                    'cover_image',
                    'alt_text',
                ),
            },
        ),
        (
            'تنظیمات مقاله',
            {
                'fields': (
                    'read_time',
                    'is_featured',
                    'is_published',
                    'published_at',
                ),
            },
        ),
        (
            'آمار',
            {
                'fields': (
                    'views',
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