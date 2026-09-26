from datetime import timedelta
from secrets import randbelow

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from orders.forms import AddressForm
from orders.models import Order
from store.models import Favorite
from support.models import Ticket

from .forms import (
    LoginOTPForm,
    ProfileForm,
    RegisterOTPForm,
    VerifyOTPForm,
)
from .models import Address, OTPCode, User


def login_page(request):
    return render(
        request,
        'loginnn.html',
    )


def generate_otp(phone, purpose):
    OTPCode.objects.filter(
        phone=phone,
        purpose=purpose,
        is_used=False,
    ).update(
        is_used=True,
    )

    code = str(
        randbelow(900000) + 100000
    )

    OTPCode.objects.create(
        phone=phone,
        code=code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=2),
    )

    print('\n' + '=' * 40)
    print(f'OTP for {phone}: {code}')
    print('=' * 40 + '\n')

    return code


@require_POST
def login_request_otp(request):

    form = LoginOTPForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'شماره موبایل صحیح نیست.',
            },
            status=400,
        )

    phone = form.cleaned_data['phone']

    user = User.objects.filter(
        phone=phone,
        is_active=True,
    ).first()

    if not user:
        return JsonResponse(
            {
                'success': False,
                'message': 'حسابی با این شماره موبایل وجود ندارد.',
            },
            status=400,
        )

    generate_otp(
        phone,
        OTPCode.LOGIN,
    )

    return JsonResponse(
        {
            'success': True,
            'message': 'کد ورود ارسال شد.',
            'phone': phone,
        }
    )


@require_POST
def register_request_otp(request):

    form = RegisterOTPForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'اطلاعات وارد شده صحیح نیست.',
            },
            status=400,
        )

    full_name = form.cleaned_data['full_name']
    phone = form.cleaned_data['phone']

    if User.objects.filter(phone=phone).exists():
        return JsonResponse(
            {
                'success': False,
                'message': 'این شماره موبایل قبلاً ثبت نام کرده است.',
            },
            status=400,
        )

    request.session['register_full_name'] = full_name
    request.session['register_phone'] = phone

    generate_otp(
        phone,
        OTPCode.REGISTER,
    )

    return JsonResponse(
        {
            'success': True,
            'message': 'کد تایید ارسال شد.',
            'phone': phone,
        }
    )


@require_POST
def verify_otp(request):

    form = VerifyOTPForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'کد وارد شده صحیح نیست.',
            },
            status=400,
        )

    phone = form.cleaned_data['phone']
    code = form.cleaned_data['code']
    purpose = request.POST.get('purpose')

    if purpose not in (
        OTPCode.LOGIN,
        OTPCode.REGISTER,
    ):
        return JsonResponse(
            {
                'success': False,
                'message': 'نوع درخواست نامعتبر است.',
            },
            status=400,
        )

    otp = (
        OTPCode.objects
        .filter(
            phone=phone,
            purpose=purpose,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
        .order_by('-created_at')
        .first()
    )

    if not otp:
        return JsonResponse(
            {
                'success': False,
                'message': 'کد منقضی شده یا وجود ندارد.',
            },
            status=400,
        )

    if otp.code != code:
        return JsonResponse(
            {
                'success': False,
                'message': 'کد تایید اشتباه است.',
            },
            status=400,
        )

    otp.is_used = True
    otp.save(update_fields=['is_used'])

    if purpose == OTPCode.LOGIN:

        user = User.objects.get(
            phone=phone,
        )

    else:

        full_name = request.session.get(
            'register_full_name',
        )

        session_phone = request.session.get(
            'register_phone',
        )

        if not full_name or session_phone != phone:
            return JsonResponse(
                {
                    'success': False,
                    'message': 'اطلاعات ثبت نام پیدا نشد.',
                },
                status=400,
            )

        user = User.objects.create_user(
            phone=phone,
            full_name=full_name,
        )

        request.session.pop(
            'register_full_name',
            None,
        )

        request.session.pop(
            'register_phone',
            None,
        )

    login(
        request,
        user,
    )

    return JsonResponse(
        {
            'success': True,
            'message': 'ورود با موفقیت انجام شد.',
            'redirect_url': reverse('dashboard'),
        }
    )


@login_required
def dashboard(request):

    user = request.user

    user_orders = (
        Order.objects
        .filter(user=user)
        .order_by('-created_at')
    )

    active_statuses = [
        Order.STATUS_PENDING,
        Order.STATUS_PAID,
        Order.STATUS_SHIPPING,
    ]

    tickets = (
        Ticket.objects
        .filter(user=user)
        .order_by('-created_at')
    )

    favorites = (
        Favorite.objects
        .filter(user=user)
        .select_related('product')
        .order_by('-created_at')
    )

    dashboard_user = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'email': user.email,
        'avatar_url': (
            user.avatar.url
            if user.avatar
            else ''
        ),
        'initials': user.initials,
        'role': (
            'مدیر'
            if user.is_staff
            else 'مشتری'
        ),
    }

    dashboard_stats = {
        'total_orders': user_orders.count(),

        'active_orders': user_orders.filter(
            status__in=active_statuses
        ).count(),

        'open_tickets': tickets.filter(
            status__in=[
                Ticket.STATUS_OPEN,
                Ticket.STATUS_IN_PROGRESS,
            ]
        ).count(),

        'favorites_count': favorites.count(),
    }

    return render(
        request,
        'dashbordd.html',
        {
            'dashboard_user': dashboard_user,
            'dashboard_stats': dashboard_stats,
            'recent_orders': user_orders[:5],
            'orders': user_orders,
            'recent_tickets': tickets[:5],
            'tickets': tickets,
            'recent_favorites': favorites[:5],
            'favorites': favorites,
            'addresses': user.addresses.all(),
            'profile': user,
        },
    )


@login_required
@require_POST
def update_profile(request):

    form = ProfileForm(
        request.POST,
        request.FILES,
        instance=request.user,
    )

    if form.is_valid():
        form.save()

    return redirect('dashboard')


@login_required
@require_POST
def create_address(request):

    form_data = request.POST.copy()

    form = AddressForm(
        form_data,
    )

    if form.is_valid():

        address = form.save(
            commit=False,
        )

        address.user = request.user

        if address.is_default:
            Address.objects.filter(
                user=request.user,
                is_default=True,
            ).update(
                is_default=False,
            )

        address.save()

    return redirect('dashboard')


@login_required
@require_POST
def edit_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    form = AddressForm(
        request.POST,
        instance=address,
    )

    if form.is_valid():

        if form.cleaned_data['is_default']:
            Address.objects.filter(
                user=request.user,
                is_default=True,
            ).exclude(
                id=address.id,
            ).update(
                is_default=False,
            )

        form.save()

    return redirect('dashboard')


@login_required
@require_POST
def delete_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    address.delete()

    return redirect('dashboard')


@login_required
def logout_view(request):

    logout(request)

    return redirect('login')