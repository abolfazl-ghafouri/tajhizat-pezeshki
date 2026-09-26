from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, CouponForm
from .models import Cart, CartItem, Coupon, Order, OrderItem


def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(
        user=user
    )

    return cart


def format_price(price):
    return f'{price:,} تومان'


def get_cart_summary(cart, coupon=None):

    items_total = cart.items_total
    discount = 0

    if coupon:

        discount = (
            items_total * coupon.discount_percent // 100
        )

    final_total = items_total - discount

    return {
        'items_total': items_total,
        'items_total_display': format_price(
            items_total
        ),

        'discount': discount,
        'discount_display': format_price(
            discount
        ),

        'final_total': final_total,
        'final_total_display': format_price(
            final_total
        ),
    }


def get_active_coupon(request):

    coupon_code = request.session.get(
        'coupon_code'
    )

    if not coupon_code:
        return None

    coupon = Coupon.objects.filter(
        code=coupon_code,
        is_active=True,
    ).first()

    if not coupon:
        request.session.pop(
            'coupon_code',
            None
        )
        return None

    if (
        coupon.expires_at
        and coupon.expires_at <= timezone.now()
    ):
        request.session.pop(
            'coupon_code',
            None
        )
        return None

    return coupon


@login_required
def cart(request):

    user_cart = get_user_cart(
        request.user
    )

    cart_items = (
        user_cart.items
        .select_related('product')
        .order_by('id')
    )

    coupon = get_active_coupon(request)

    items = []

    for item in cart_items:

        product = item.product

        items.append({
            'id': item.id,
            'title': product.title,
            'sku': product.sku,
            'image_url': (
                product.main_image.url
                if product.main_image
                else ''
            ),
            'warranty_text': product.warranty_text,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'unit_price_display': format_price(
                item.unit_price
            ),
            'discount_percent': (
                product.discount_percent
            ),
            'total': item.total_price,
            'total_display': format_price(
                item.total_price
            ),
        })

    summary = get_cart_summary(
        user_cart,
        coupon,
    )

    coupon_data = None

    if coupon:

        coupon_data = {
            'code': coupon.code,
            'discount_percent': coupon.discount_percent,
            'message': (
                f'کد تخفیف {coupon.code} اعمال شد.'
            ),
        }

    context = {
        'cart_items': items,
        'cart_summary': summary,
        'coupon': coupon_data,
    }

    return render(
        request,
        'sabadkharid.html',
        context,
    )


@login_required
@require_POST
def add_to_cart(request, product_id):

    from store.models import Product

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    if product.stock <= 0:

        return JsonResponse({
            'success': False,
            'message': 'این محصول موجود نیست.',
        }, status=400)

    try:
        quantity = int(
            request.POST.get(
                'quantity',
                1
            )
        )
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    user_cart = get_user_cart(
        request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=user_cart,
        product=product,
    )

    new_quantity = (
        quantity
        if created
        else cart_item.quantity + quantity
    )

    if new_quantity > product.stock:

        if created:
            cart_item.delete()

        return JsonResponse({
            'success': False,
            'message': (
                f'حداکثر تعداد قابل سفارش '
                f'{product.stock} عدد است.'
            ),
        }, status=400)

    cart_item.quantity = new_quantity
    cart_item.save()

    return JsonResponse({
        'success': True,
        'message': 'محصول به سبد خرید اضافه شد.',
        'cart_count': user_cart.total_items,
    })


@login_required
@require_POST
def update_cart_item(
    request,
    item_id,
):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    try:
        quantity = int(
            request.POST.get(
                'quantity',
                1
            )
        )
    except (TypeError, ValueError):
        return JsonResponse({
            'success': False,
            'message': 'تعداد وارد شده صحیح نیست.',
        }, status=400)

    if quantity < 1:

        cart_item.delete()

        return JsonResponse({
            'success': True,
            'deleted': True,
            'message': 'محصول حذف شد.',
        })

    if quantity > cart_item.product.stock:

        return JsonResponse({
            'success': False,
            'message': (
                f'حداکثر تعداد قابل سفارش '
                f'{cart_item.product.stock} عدد است.'
            ),
        }, status=400)

    cart_item.quantity = quantity
    cart_item.save()

    coupon = get_active_coupon(
        request
    )

    summary = get_cart_summary(
        cart_item.cart,
        coupon,
    )

    return JsonResponse({
        'success': True,
        'item_total': cart_item.total_price,
        'item_total_display': format_price(
            cart_item.total_price
        ),
        'summary': summary,
    })


@login_required
@require_POST
def remove_from_cart(
    request,
    item_id,
):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    cart = cart_item.cart

    cart_item.delete()

    coupon = get_active_coupon(
        request
    )

    summary = get_cart_summary(
        cart,
        coupon,
    )

    return JsonResponse({
        'success': True,
        'message': 'محصول از سبد حذف شد.',
        'cart_count': cart.total_items,
        'summary': summary,
    })


@login_required
@require_POST
def apply_coupon(request):

    form = CouponForm(
        request.POST
    )

    if not form.is_valid():

        return JsonResponse({
            'success': False,
            'message': 'کد تخفیف را وارد کنید.',
        }, status=400)

    code = form.cleaned_data['code']

    coupon = Coupon.objects.filter(
        code=code,
        is_active=True,
    ).first()

    if not coupon:

        return JsonResponse({
            'success': False,
            'message': 'کد تخفیف معتبر نیست.',
        }, status=400)

    if (
        coupon.expires_at
        and coupon.expires_at <= timezone.now()
    ):

        return JsonResponse({
            'success': False,
            'message': 'کد تخفیف منقضی شده است.',
        }, status=400)

    user_cart = get_user_cart(
        request.user
    )

    if not user_cart.items.exists():

        return JsonResponse({
            'success': False,
            'message': 'سبد خرید شما خالی است.',
        }, status=400)

    request.session['coupon_code'] = coupon.code

    summary = get_cart_summary(
        user_cart,
        coupon,
    )

    return JsonResponse({
        'success': True,
        'message': (
            f'کد {coupon.code} با موفقیت اعمال شد.'
        ),
        'discount_percent': coupon.discount_percent,
        'summary': summary,
    })


@login_required
@require_POST
def remove_coupon(request):

    request.session.pop(
        'coupon_code',
        None
    )

    user_cart = get_user_cart(
        request.user
    )

    summary = get_cart_summary(
        user_cart
    )

    return JsonResponse({
        'success': True,
        'message': 'کد تخفیف حذف شد.',
        'summary': summary,
    })


@login_required
def checkout(request):

    user_cart = get_user_cart(
        request.user
    )

    cart_items = (
        user_cart.items
        .select_related('product')
        .all()
    )

    if not cart_items.exists():

        return redirect('cart')

    coupon = get_active_coupon(
        request
    )

    if request.method == 'GET':

        form = CheckoutForm(
            initial={
                'customer_name': (
                    request.user.full_name
                ),
                'phone': request.user.phone,
            }
        )

    else:

        form = CheckoutForm(
            request.POST
        )

        if form.is_valid():

            with transaction.atomic():

                total_amount = 0

                order_items = []

                for cart_item in cart_items:

                    product = cart_item.product

                    if not product.is_active:
                        raise ValueError(
                            f'محصول {product.title} فعال نیست.'
                        )

                    if product.stock < cart_item.quantity:
                        raise ValueError(
                            f'موجودی {product.title} کافی نیست.'
                        )

                    unit_price = product.final_price

                    item_total = (
                        unit_price
                        * cart_item.quantity
                    )

                    total_amount += item_total

                    order_items.append({
                        'product': product,
                        'title': product.title,
                        'sku': product.sku,
                        'unit_price': unit_price,
                        'quantity': cart_item.quantity,
                        'total_price': item_total,
                    })

                discount_amount = 0

                if coupon:

                    discount_amount = (
                        total_amount
                        * coupon.discount_percent
                        // 100
                    )

                final_amount = (
                    total_amount
                    - discount_amount
                )

                order = Order.objects.create(
                    user=request.user,

                    number=(
                        f'ORD-{timezone.now():%Y%m%d}'
                        f'-{uuid4().hex[:8].upper()}'
                    ),

                    status=Order.STATUS_PENDING,

                    total_amount=total_amount,

                    discount_amount=discount_amount,

                    final_amount=final_amount,

                    recipient_name=(
                        form.cleaned_data[
                            'customer_name'
                        ]
                    ),

                    phone=(
                        form.cleaned_data[
                            'phone'
                        ]
                    ),

                    province='',

                    city=(
                        form.cleaned_data[
                            'city'
                        ]
                    ),

                    address=(
                        form.cleaned_data[
                            'address'
                        ]
                    ),

                    postal_code=(
                        form.cleaned_data[
                            'postal_code'
                        ]
                    ),
                )

                for item in order_items:

                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_title=item['title'],
                        sku=item['sku'],
                        unit_price=item['unit_price'],
                        quantity=item['quantity'],
                        total_price=item['total_price'],
                    )

                    item['product'].stock -= (
                        item['quantity']
                    )

                    item['product'].save(
                        update_fields=['stock']
                    )

                user_cart.items.all().delete()

                request.session.pop(
                    'coupon_code',
                    None
                )

            return render(
                request,
                'sabadkharid.html',
                {
                    'order_success': True,
                    'order': order,
                    'cart_items': [],
                    'cart_summary': {
                        'items_total_display': '۰ تومان',
                        'discount_display': '۰ تومان',
                        'final_total_display': '۰ تومان',
                    },
                }
            )

    cart_items_data = []

    for item in cart_items:

        product = item.product

        cart_items_data.append({
            'id': item.id,
            'title': product.title,
            'sku': product.sku,
            'image_url': (
                product.main_image.url
                if product.main_image
                else ''
            ),
            'warranty_text': product.warranty_text,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'unit_price_display': format_price(
                item.unit_price
            ),
            'discount_percent': (
                product.discount_percent
            ),
            'total_display': format_price(
                item.total_price
            ),
        })

    context = {
        'cart_items': cart_items_data,

        'cart_summary': get_cart_summary(
            user_cart,
            coupon,
        ),

        'coupon': (
            {
                'code': coupon.code,
                'discount_percent': coupon.discount_percent,
                'message': (
                    f'کد {coupon.code} اعمال شده است.'
                ),
            }
            if coupon
            else None
        ),

        'checkout_form': form,
    }

    return render(
        request,
        'sabadkharid.html',
        context,
    )


@login_required
def order_detail(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items'
        ),
        number=order_number,
        user=request.user,
    )

    return render(
        request,
        'dashbordd.html',
        {
            'order_detail': order,
        },
    )