from django.urls import path

from . import views


urlpatterns = [
    path(
        'cart/',
        views.cart,
        name='cart',
    ),

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart',
    ),

    path(
        'cart/update/<int:item_id>/',
        views.update_cart_item,
        name='update_cart_item',
    ),

    path(
        'cart/remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart',
    ),

    path(
        'cart/coupon/',
        views.apply_coupon,
        name='apply_coupon',
    ),

    path(
        'cart/coupon/remove/',
        views.remove_coupon,
        name='remove_coupon',
    ),

    path(
        'checkout/',
        views.checkout,
        name='checkout',
    ),

    path(
        'orders/<str:order_number>/',
        views.order_detail,
        name='order_detail',
    ),

    path(
        'payment/start/<str:order_number>/',
        views.start_payment,
        name='start_payment',
    ),

    path(
        'payment/zarinpal/verify/',
        views.zarinpal_verify,
        name='zarinpal_verify',
    ),

    path(
        'payment/success/<str:order_number>/',
        views.payment_success,
        name='payment_success',
    ),
]