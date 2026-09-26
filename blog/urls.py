from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.blog,
        name='blog',
    ),

    path(
        '<slug:slug>/',
        views.article_detail,
        name='article_detail',
    ),

    path(
        '<int:article_id>/comment/',
        views.add_article_comment,
        name='add_article_comment',
    ),
]