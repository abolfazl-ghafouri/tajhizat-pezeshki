from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import NewsletterForm
from .models import (
    CompanyStat,
    FAQ,
    NewsletterSubscriber,
    ServiceFeature,
    SiteSettings,
    TeamMember,
)


def about(request):

    site_settings = (
        SiteSettings.objects.first()
    )

    company_stats = (
        CompanyStat.objects
        .filter(
            is_active=True
        )
        .order_by('order')
    )

    team_members = (
        TeamMember.objects
        .filter(
            is_active=True
        )
        .order_by('order')
    )

    return render(
        request,
        'darbarema.html',
        {
            'site_settings': site_settings,
            'company_stats': company_stats,
            'team_members': team_members,
        },
    )


@require_POST
def subscribe_newsletter(request):

    form = NewsletterForm(
        request.POST
    )

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': 'ایمیل صحیح نیست.',
                'errors': form.errors,
            },
            status=400,
        )

    email = form.cleaned_data['email']

    subscriber = (
        NewsletterSubscriber.objects
        .filter(email=email)
        .first()
    )

    if subscriber:

        if not subscriber.is_active:

            subscriber.is_active = True
            subscriber.save(
                update_fields=['is_active']
            )

            return JsonResponse({
                'success': True,
                'message': 'عضویت شما فعال شد.',
            })

        return JsonResponse({
            'success': True,
            'message': (
                'این ایمیل قبلاً عضو خبرنامه شده است.'
            ),
        })

    NewsletterSubscriber.objects.create(
        email=email
    )

    return JsonResponse({
        'success': True,
        'message': (
            'با موفقیت در خبرنامه عضو شدید.'
        ),
    })


def faq_list(request):

    faqs = (
        FAQ.objects
        .filter(
            is_active=True
        )
        .order_by('order')
    )

    return render(
        request,
        'darbarema.html',
        {
            'faqs': faqs,
        },
    )