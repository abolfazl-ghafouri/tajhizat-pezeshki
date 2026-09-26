from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Address, OTPCode, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        'phone',
        'full_name',
        'email',
        'is_active',
        'is_staff',
        'date_joined',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'phone',
        'full_name',
        'email',
    )

    ordering = (
        '-date_joined',
    )

    fieldsets = (
        (
            'اطلاعات کاربر',
            {
                'fields': (
                    'phone',
                    'full_name',
                    'email',
                    'avatar',
                    'password',
                )
            }
        ),
        (
            'دسترسی‌ها',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),
        (
            'اطلاعات زمانی',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                )
            }
        ),
    )

    add_fieldsets = (
        (
            'ایجاد کاربر',
            {
                'classes': ('wide',),
                'fields': (
                    'phone',
                    'full_name',
                    'email',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                ),
            }
        ),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):

    list_display = (
        'phone',
        'code',
        'purpose',
        'created_at',
        'expires_at',
        'is_used',
    )

    list_filter = (
        'purpose',
        'is_used',
        'created_at',
    )

    search_fields = (
        'phone',
        'code',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'recipient_name',
        'phone',
        'province',
        'city',
        'is_default',
        'created_at',
    )

    list_filter = (
        'province',
        'city',
        'is_default',
    )

    search_fields = (
        'user__phone',
        'recipient_name',
        'phone',
        'city',
        'postal_code',
    )

    ordering = (
        '-created_at',
    )