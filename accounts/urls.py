from django.urls import path

from . import views


urlpatterns = [
    path(
        'login/',
        views.login_page,
        name='login',
    ),

    path(
        'login/request-otp/',
        views.login_request_otp,
        name='login_request_otp',
    ),

    path(
        'register/request-otp/',
        views.register_request_otp,
        name='register_request_otp',
    ),

    path(
        'verify-otp/',
        views.verify_otp,
        name='verify_otp',
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout',
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard',
    ),

    path(
        'profile/update/',
        views.update_profile,
        name='update_profile',
    ),

    path(
        'addresses/create/',
        views.create_address,
        name='create_address',
    ),

    path(
        'addresses/<int:address_id>/edit/',
        views.edit_address,
        name='edit_address',
    ),

    path(
        'addresses/<int:address_id>/delete/',
        views.delete_address,
        name='delete_address',
    ),
]