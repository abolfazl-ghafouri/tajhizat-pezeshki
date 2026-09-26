from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .forms import (
    ConsultationRequestForm,
    ContactMessageForm,
    TicketForm,
)
from .models import (
    ConsultationRequest,
    ContactMessage,
    Ticket,
)


def generate_ticket_number():
    last_ticket = (
        Ticket.objects
        .order_by('-id')
        .first()
    )

    if not last_ticket:
        number = 1
    else:
        number = last_ticket.id + 1

    return f'TKT-{number:06d}'


@require_POST
def send_contact_message(request):

    form = ContactMessageForm(
        request.POST
    )

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'اطلاعات فرم صحیح نیست.',
                'errors': form.errors,
            },
            status=400,
        )

    contact = form.save(
        commit=False
    )

    if request.user.is_authenticated:
        contact.user = request.user

    contact.save()

    return JsonResponse(
        {
            'success': True,
            'message': (
                'پیام شما با موفقیت ارسال شد.'
            ),
        }
    )


@require_POST
def request_consultation(request):

    form = ConsultationRequestForm(
        request.POST
    )

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'اطلاعات درخواست صحیح نیست.',
                'errors': form.errors,
            },
            status=400,
        )

    consultation = form.save(
        commit=False
    )

    if request.user.is_authenticated:
        consultation.user = request.user

    consultation.save()

    return JsonResponse(
        {
            'success': True,
            'message': (
                'درخواست مشاوره شما ثبت شد.'
            ),
        }
    )


@login_required
@require_POST
def create_ticket(request):

    form = TicketForm(
        request.POST
    )

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'اطلاعات تیکت صحیح نیست.',
                'errors': form.errors,
            },
            status=400,
        )

    ticket = form.save(
        commit=False
    )

    ticket.user = request.user

    ticket.number = generate_ticket_number()

    ticket.save()

    return JsonResponse(
        {
            'success': True,
            'message': (
                'تیکت شما با موفقیت ثبت شد.'
            ),
            'ticket_number': ticket.number,
        }
    )


@login_required
def ticket_list(request):

    tickets = (
        Ticket.objects
        .filter(
            user=request.user
        )
        .select_related(
            'related_product'
        )
        .order_by(
            '-created_at'
        )
    )

    return {
        'tickets': tickets,
    }