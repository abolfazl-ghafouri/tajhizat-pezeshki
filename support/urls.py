from django.urls import path

from . import views


urlpatterns = [
    path(
        'contact/',
        views.send_contact_message,
        name='send_contact_message',
    ),

    path(
        'consultation/',
        views.request_consultation,
        name='request_consultation',
    ),

    path(
        'tickets/create/',
        views.create_ticket,
        name='create_ticket',
    ),
]