from uuid import uuid4

from accounts.models import Address

import requests

from django.conf import settings
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, CouponForm
from .models import Cart, CartItem, Coupon, Order, OrderItem



def zarinpal_request_payment(
    order,
    request,
):

    amount = order.final_amount * 10

    callback_url = request.build_absolute_uri(
        reverse(
            'zarinpal_verify'
        )
    )

    data = {
        'merchant_id': settings.ZARINPAL_MERCHANT_ID,
        'amount': amount,
        'description': (
            f'پرداخت سفارش {order.number}'
        ),
        'callback_url': callback_url,
        'metadata': {
            'mobile': order.phone,
        },
    }

    try:

        response = requests.post(
            settings.ZARINPAL_SANDBOX_REQUEST_URL,
            json=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'ZarinPal Rest Api v1',
            },
            timeout=15,
        )

    except requests.RequestException as error:

        print('\n' + '=' * 60)
        print('ZARINPAL REQUEST ERROR:')
        print(error)
        print('=' * 60 + '\n')

        return None

    print('\n' + '=' * 60)
    print(
        'ZARINPAL REQUEST STATUS:',
        response.status_code
    )
    print(
        'ZARINPAL REQUEST CONTENT-TYPE:',
        response.headers.get('Content-Type')
    )
    print('ZARINPAL REQUEST RESPONSE:')
    print(response.text)
    print('=' * 60 + '\n')

    try:

        result = response.json()

    except ValueError:

        print(
            'ZARINPAL REQUEST RESPONSE IS NOT JSON.'
        )

        return None

    if (
        response.ok
        and not result.get('errors')
        and result.get('data', {}).get('code') == 100
    ):

        authority = (
            result['data']['authority']
        )

        order.payment_authority = authority

        order.save(
            update_fields=[
                'payment_authority',
            ]
        )

        return (
            settings.ZARINPAL_SANDBOX_STARTPAY_URL
            + authority
        )

    print('\n' + '=' * 60)
    print('ZARINPAL REQUEST FAILED:')
    print(result)
    print('=' * 60 + '\n')

    return None


def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(
        user=user
    )

    return cart


def to_persian_digits(value):
    translation = str.maketrans(
        '0123456789',
        '۰۱۲۳۴۵۶۷۸۹'
    )
    return str(value).translate(translation)


def format_price(price):
    formatted = f'{price:,}'
    formatted = formatted.replace(',', '٬')

    return f'{to_persian_digits(formatted)} تومان'


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

    # ---------------- CHECKOUT FORM ----------------

    default_address = (
        Address.objects
        .filter(
            user=request.user,
            is_default=True,
        )
        .first()
    )

    initial_data = {
        'customer_name': request.user.full_name,
        'phone': request.user.phone,
        'city': '',
        'address': '',
        'postal_code': '',
    }

    if default_address:
        initial_data.update({
            'city': default_address.city,
            'address': default_address.address,
            'postal_code': default_address.postal_code,
        })

    checkout_form = CheckoutForm(
        initial=initial_data
    )

    context = {
        'cart_items': items,
        'cart_summary': summary,
        'coupon': coupon_data,
        'checkout_form': checkout_form,
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

    # ------------------------------------------
    # دریافت سبد خرید کاربر
    # ------------------------------------------

    user_cart = get_user_cart(
        request.user
    )

    cart_items = (
        user_cart.items
        .select_related('product')
        .all()
    )

    # اگر سبد خالی است
    if not cart_items.exists():
        return redirect('cart')

    # ------------------------------------------
    # دریافت کوپن فعال
    # ------------------------------------------

    coupon = get_active_coupon(
        request
    )

    # ------------------------------------------
    # دریافت آدرس پیش فرض کاربر
    # ------------------------------------------

    default_address = (
        Address.objects
        .filter(
            user=request.user,
            is_default=True,
        )
        .first()
    )

    # ------------------------------------------
    # اطلاعات اولیه فرم
    # ------------------------------------------

    initial_data = {
        'customer_name': request.user.full_name,
        'phone': request.user.phone,
        'city': '',
        'address': '',
        'postal_code': '',
    }

    if default_address:

        initial_data.update({
            'city': default_address.city,
            'address': default_address.address,
            'postal_code': default_address.postal_code,
        })

    # ------------------------------------------
    # GET
    # ------------------------------------------

    if request.method == 'GET':

        form = CheckoutForm(
            initial=initial_data
        )

    # ------------------------------------------
    # POST
    # ------------------------------------------

    else:

        form = CheckoutForm(
            request.POST
        )

        # --------------------------------------
        # اعتبارسنجی فرم
        # --------------------------------------

        if form.is_valid():

            # ----------------------------------
            # بررسی موجودی قبل از ساخت سفارش
            # ----------------------------------

            for cart_item in cart_items:

                product = cart_item.product

                if not product.is_active:

                    form.add_error(
                        None,
                        f'محصول «{product.title}» دیگر فعال نیست.',
                    )

                    break

                if product.stock < cart_item.quantity:

                    form.add_error(
                        None,
                        (
                            f'موجودی محصول '
                            f'«{product.title}» کافی نیست.'
                        ),
                    )

                    break

            # اگر مشکل موجودی داشتیم
            if form.errors:
                pass

            else:

                # ------------------------------
                # محاسبه مبلغ سفارش
                # ------------------------------

                total_amount = 0

                order_items_data = []

                for cart_item in cart_items:

                    product = cart_item.product

                    unit_price = (
                        product.final_price
                    )

                    item_total = (
                        unit_price
                        * cart_item.quantity
                    )

                    total_amount += item_total

                    order_items_data.append({
                        'product': product,
                        'product_title': product.title,
                        'sku': product.sku,
                        'unit_price': unit_price,
                        'quantity': cart_item.quantity,
                        'total_price': item_total,
                    })

                # ------------------------------
                # محاسبه تخفیف
                # ------------------------------

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

                # ------------------------------
                # ساخت سفارش
                # ------------------------------

                with transaction.atomic():

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

                        province=(
                            default_address.province
                            if default_address
                            else ''
                        ),

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

                    # --------------------------
                    # ساخت Order Items
                    # --------------------------

                    for item in order_items_data:

                        OrderItem.objects.create(

                            order=order,

                            product=item['product'],

                            product_title=(
                                item['product_title']
                            ),

                            sku=item['sku'],

                            unit_price=(
                                item['unit_price']
                            ),

                            quantity=item['quantity'],

                            total_price=(
                                item['total_price']
                            ),
                        )

                # ----------------------------------
                # سفارش ساخته شد
                # ----------------------------------
                #
                # هنوز:
                # stock کم نمی‌کنیم
                # cart خالی نمی‌کنیم
                #
                # چون پرداخت هنوز انجام نشده است.
                # ----------------------------------

                return redirect(
                    'start_payment',
                    order_number=order.number,
                )

    # ------------------------------------------
    # آماده‌سازی اطلاعات سبد برای Template
    # ------------------------------------------

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

            'warranty_text': (
                product.warranty_text
            ),

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

    # ------------------------------------------
    # Context
    # ------------------------------------------

    context = {

        'cart_items': cart_items_data,

        'cart_summary': get_cart_summary(
            user_cart,
            coupon,
        ),

        'coupon': (
            {
                'code': coupon.code,
                'discount_percent': (
                    coupon.discount_percent
                ),
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


@login_required
def payment_success(request, order_number):

    order = get_object_or_404(
        Order,
        number=order_number,
        user=request.user,
    )

    if order.status != Order.STATUS_PAID:
        return redirect(
            'order_detail',
            order_number=order.number,
        )

    return render(
        request,
        'payment_success.html',
        {
            'order': order,
            'final_amount_display': format_price(
                order.final_amount
            ),
        },
    )

@login_required
def payment_success(request, order_number):

    order = get_object_or_404(
        Order,
        number=order_number,
        user=request.user,
    )

    if order.status != Order.STATUS_PAID:
        return redirect(
            'order_detail',
            order_number=order.number,
        )

    return render(
        request,
        'payment_success.html',
        {
            'order': order,
            'final_amount_display': format_price(
                order.final_amount
            ),
        },
    )


@login_required
def start_payment(
    request,
    order_number,
):
    order = get_object_or_404(
        Order,
        number=order_number,
        user=request.user,
    )

    if order.status != Order.STATUS_PENDING:
        return redirect(
            'order_detail',
            order_number=order.number,
        )

    payment_url = zarinpal_request_payment(
        order,
        request,
    )

    if not payment_url:
        return render(
            request,
            'sabadkharid.html',
            {
                'payment_error': (
                    'خطا در اتصال به درگاه آزمایشی زرین‌پال.'
                ),
            },
        )

    return redirect(payment_url)


def zarinpal_verify(request):

    authority = request.GET.get(
        'Authority'
    )

    status = request.GET.get(
        'Status'
    )

    if not authority:
        return render(
            request,
            'sabadkharid.html',
            {
                'payment_error': (
                    'اطلاعات بازگشت از درگاه ناقص است.'
                ),
            },
        )

    order = Order.objects.filter(
        payment_authority=authority
    ).first()

    if not order:
        return render(
            request,
            'sabadkharid.html',
            {
                'payment_error': (
                    'سفارش مربوط به این پرداخت پیدا نشد.'
                ),
            },
        )

    if status != 'OK':
        order.status = Order.STATUS_CANCELLED

        order.save(
            update_fields=[
                'status',
                'updated_at',
            ]
        )

        return render(
            request,
            'payment_cancelled.html',
            {
                'order': order,
            },
        )

    amount = order.final_amount * 10

    data = {
        'merchant_id': settings.ZARINPAL_MERCHANT_ID,
        'amount': amount,
        'authority': authority,
    }

    response = requests.post(
        settings.ZARINPAL_SANDBOX_VERIFY_URL,
        json=data,
        headers={
            'User-Agent': 'ZarinPal Rest API v1',
        },
        timeout=15,
    )

    print('\n' + '=' * 60)
    print('ZARINPAL VERIFY STATUS:', response.status_code)
    print('ZARINPAL VERIFY CONTENT-TYPE:', response.headers.get('Content-Type'))
    print('ZARINPAL VERIFY RESPONSE:')
    print(response.text)
    print('=' * 60 + '\n')

    try:
        result = response.json()

    except ValueError:
        return render(
            request,
            'sabadkharid.html',
            {
                'payment_failed': True,
                'order': order,
                'payment_error': (
                    'پاسخ معتبری از سرویس تأیید پرداخت دریافت نشد.'
                ),
            },
        )

    payment_code = (
        result.get('data', {})
        .get('code')
    )

    if payment_code not in [100, 101]:
        return render(
            request,
            'sabadkharid.html',
            {
                'payment_failed': True,
                'order': order,
            },
        )

    ref_id = (
        result.get('data', {})
        .get('ref_id')
    )

    with transaction.atomic():

        order = (
            Order.objects
            .select_for_update()
            .get(
                id=order.id
            )
        )

        if order.status != Order.STATUS_PAID:

            for item in order.items.select_related(
                'product'
            ):

                product = item.product

                if not product:
                    continue

                if product.stock < item.quantity:
                    order.status = (
                        Order.STATUS_CANCELLED
                    )
                    order.save(
                        update_fields=[
                            'status',
                            'updated_at',
                        ]
                    )

                    return render(
                        request,
                        'sabadkharid.html',
                        {
                            'payment_failed': True,
                            'order': order,
                            'payment_error': (
                                'موجودی محصول برای تکمیل سفارش کافی نیست.'
                            ),
                        },
                    )

                product.stock -= item.quantity

                product.save(
                    update_fields=[
                        'stock'
                    ]
                )

            order.status = Order.STATUS_PAID

            order.payment_ref_id = (
                str(ref_id)
                if ref_id
                else ''
            )

            order.paid_at = timezone.now()

            order.save(
                update_fields=[
                    'status',
                    'payment_ref_id',
                    'paid_at',
                    'updated_at',
                ]
            )

            user_cart = get_user_cart(
                order.user
            )

            user_cart.items.all().delete()

            return redirect(
                'payment_success',
                order_number=order.number,
            )

        return redirect(
            'payment_success',
            order_number=order.number,
        )