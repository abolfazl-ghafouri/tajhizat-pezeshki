from django.urls import path

from . import views


urlpatterns = [
    path(
        'about/',
        views.about,
        name='about',
    ),

    path(
        'newsletter/subscribe/',
        views.subscribe_newsletter,
        name='newsletter_subscribe',
    ),

    path(
        'faq/',
        views.faq_list,
        name='faq_list',
    ),
]