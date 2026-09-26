from django.contrib import admin

from .models import (
    ContactMessage,
    ConsultationRequest,
    Ticket,
)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'number',
        'user',
        'subject',
        'category',
        'priority',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'category',
        'created_at',
    )

    search_fields = (
        'number',
        'subject',
        'message',
        'user__phone',
        'user__full_name',
    )

    list_editable = (
        'priority',
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
            'اطلاعات تیکت',
            {
                'fields': (
                    'number',
                    'user',
                    'subject',
                    'category',
                    'priority',
                    'status',
                ),
            },
        ),
        (
            'محتوا',
            {
                'fields': (
                    'message',
                    'related_product',
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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        'subject',
        'name',
        'email',
        'phone',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'name',
        'email',
        'phone',
        'subject',
        'message',
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'phone',
        'product',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'name',
        'phone',
        'email',
        'message',
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )

    fieldsets = (
        (
            'اطلاعات مشتری',
            {
                'fields': (
                    'user',
                    'name',
                    'phone',
                    'email',
                ),
            },
        ),
        (
            'درخواست',
            {
                'fields': (
                    'product',
                    'message',
                    'status',
                ),
            },
        ),
        (
            'تاریخ',
            {
                'fields': (
                    'created_at',
                ),
            },
        ),
    )