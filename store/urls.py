from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.home,
        name='home',
    ),

    path(
        'shop/',
        views.shop,
        name='shop',
    ),

    path(
        'shop/<slug:slug>/',
        views.product_detail,
        name='product_detail',
    ),

    path(
        'shop/product/<int:product_id>/favorite/',
        views.toggle_favorite,
        name='toggle_favorite',
    ),

    path(
        'shop/product/<int:product_id>/review/',
        views.add_product_review,
        name='add_product_review',
    ),
]