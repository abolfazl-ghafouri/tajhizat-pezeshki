from django.contrib import admin

from .models import (
    CompanyStat,
    FAQ,
    NewsletterSubscriber,
    ServiceFeature,
    SiteSettings,
    TeamMember,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    list_display = (
        'site_name',
        'phone',
        'email',
        'updated_at',
    )

    readonly_fields = (
        'updated_at',
    )

    fieldsets = (
        (
            'اطلاعات سایت',
            {
                'fields': (
                    'site_name',
                    'slogan',
                    'logo',
                ),
            },
        ),
        (
            'اطلاعات تماس',
            {
                'fields': (
                    'phone',
                    'email',
                    'address',
                    'working_hours',
                ),
            },
        ),
        (
            'درباره ما',
            {
                'fields': (
                    'about_text',
                ),
            },
        ),
        (
            'تاریخ',
            {
                'fields': (
                    'updated_at',
                ),
            },
        ),
    )


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'description',
        'order',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'title',
        'description',
    )

    list_editable = (
        'order',
        'is_active',
    )

    ordering = (
        'order',
    )


@admin.register(CompanyStat)
class CompanyStatAdmin(admin.ModelAdmin):

    list_display = (
        'label',
        'value',
        'icon',
        'order',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'label',
        'value',
    )

    list_editable = (
        'value',
        'order',
        'is_active',
    )

    ordering = (
        'order',
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'role',
        'order',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'role',
        'bio',
    )

    list_editable = (
        'order',
        'is_active',
    )

    ordering = (
        'order',
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):

    list_display = (
        'question',
        'order',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'question',
        'answer',
    )

    list_editable = (
        'order',
        'is_active',
    )

    ordering = (
        'order',
    )


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):

    list_display = (
        'email',
        'is_active',
        'subscribed_at',
    )

    list_filter = (
        'is_active',
        'subscribed_at',
    )

    search_fields = (
        'email',
    )

    list_editable = (
        'is_active',
    )

    readonly_fields = (
        'subscribed_at',
    )

    ordering = (
        '-subscribed_at',
    )