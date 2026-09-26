from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from core.models import SiteSettings

from .forms import ArticleCommentForm
from .models import (
    Article,
    ArticleComment,
    BlogCategory,
    Tag,
)


def article_image(article):

    if article.cover_image:
        return article.cover_image.url

    return static(
        'images/webloggggg.jpeg'
    )


def article_data(article):

    return {
        'id': article.id,

        'title': article.title,

        'excerpt': article.excerpt,

        'image_url': article_image(
            article
        ),

        'image_alt': (
            article.alt_text
            or article.title
        ),

        'published_at_display': (
            article.published_at.strftime(
                '%Y/%m/%d'
            )
            if article.published_at
            else ''
        ),

        'read_time': article.read_time,

        'views_display': f'{article.views:,}',

        'detail_url': (
            f'/blog/{article.slug}/'
        ),

        'is_featured': article.is_featured,
    }


def blog(request):

    articles = (
        Article.objects
        .filter(
            is_published=True,
        )
        .select_related(
            'author',
            'category',
        )
        .prefetch_related(
            'tags',
        )
    )

    query = request.GET.get(
        'q',
        ''
    ).strip()

    selected_category = request.GET.get(
        'category',
        ''
    ).strip()

    selected_tag = request.GET.get(
        'tag',
        ''
    ).strip()

    # ---------------- SEARCH ----------------

    if query:

        articles = articles.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(content__icontains=query)
        )

    # ---------------- CATEGORY ----------------

    if selected_category:

        articles = articles.filter(
            category__slug=selected_category
        )

    # ---------------- TAG ----------------

    if selected_tag:

        articles = articles.filter(
            tags__slug=selected_tag
        )

    articles = articles.order_by(
        '-published_at',
        '-created_at',
    ).distinct()

    # ---------------- FEATURED ----------------

    featured_articles = articles.filter(
        is_featured=True
    )[:4]

    # ---------------- PAGINATION ----------------

    paginator = Paginator(
        articles,
        9
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    posts = [
        article_data(article)
        for article in page_obj
    ]

    # ---------------- CATEGORIES ----------------

    categories = (
        BlogCategory.objects
        .filter(
            is_active=True,
        )
        .annotate(
            count=Count(
                'articles',
                filter=Q(
                    articles__is_published=True
                )
            )
        )
        .order_by('name')
    )

    # ---------------- POPULAR POSTS ----------------

    popular_articles = (
        Article.objects
        .filter(
            is_published=True
        )
        .order_by(
            '-views',
            '-published_at',
        )[:5]
    )

    popular_posts = [
        article_data(article)
        for article in popular_articles
    ]

    # ---------------- TAGS ----------------

    tags = (
        Tag.objects
        .filter(
            articles__is_published=True
        )
        .annotate(
            article_count=Count(
                'articles',
                filter=Q(
                    articles__is_published=True
                )
            )
        )
        .distinct()
        .order_by('name')
    )

    context = {
        'site_settings': SiteSettings.objects.first(),

        'posts': posts,

        'featured_articles': [
            article_data(article)
            for article in featured_articles
        ],

        'categories': categories,

        'popular_posts': popular_posts,

        'tags': tags,

        'query': query,

        'selected_category': (
            selected_category
        ),

        'selected_tag': selected_tag,

        'pagination': page_obj,
    }

    return render(
        request,
        'weblog.html',
        context,
    )


def article_detail(
    request,
    slug,
):

    article = get_object_or_404(
        Article.objects
        .select_related(
            'author',
            'category',
        )
        .prefetch_related(
            'tags'
        ),
        slug=slug,
        is_published=True,
    )

    # افزایش بازدید
    Article.objects.filter(
        id=article.id
    ).update(
        views=article.views + 1
    )

    article.views += 1

    comments = (
        article.comments
        .filter(
            is_approved=True
        )
        .select_related(
            'user'
        )
        .order_by(
            '-created_at'
        )
    )

    related_articles = (
        Article.objects
        .filter(
            is_published=True,
            category=article.category,
        )
        .exclude(
            id=article.id
        )
        .order_by(
            '-published_at'
        )[:4]
    )

    article_data_context = {
        'id': article.id,

        'title': article.title,

        'excerpt': article.excerpt,

        'cover_url': article_image(
            article
        ),

        'cover_alt': (
            article.alt_text
            or article.title
        ),

        'published_at_display': (
            article.published_at.strftime(
                '%Y/%m/%d'
            )
            if article.published_at
            else ''
        ),

        'read_time': article.read_time,

        'category_name': (
            article.category.name
            if article.category
            else ''
        ),

        'content_html': article.content,

        'tags': article.tags.all(),

        'slug': article.slug,

        'detail_url': (
            f'/blog/{article.slug}/'
        ),

        'author_name': (
            article.author.full_name
            if article.author
            else 'مدیریت سایت'
        ),

        'views_display': (
            f'{article.views:,}'
        ),
    }

    related_data = [
        article_data(article)
        for article in related_articles
    ]

    blog_categories = (
        BlogCategory.objects
        .filter(
            is_active=True
        )
        .annotate(
            count=Count(
                'articles',
                filter=Q(
                    articles__is_published=True
                )
            )
        )
        .order_by('name')
    )

    category_icons = {
        'dental': {
            'class': 'equipment',
            'icon': 'fa-solid fa-tooth',
        },

        'medical': {
            'class': 'medical',
            'icon': 'fa-solid fa-stethoscope',
        },

        'lab': {
            'class': 'guide',
            'icon': 'fa-solid fa-flask',
        },

        'imaging': {
            'class': 'news',
            'icon': 'fa-solid fa-x-ray',
        },

        'operating-room': {
            'class': 'news',
            'icon': 'fa-solid fa-hospital',
        },

        'patient-monitoring': {
            'class': 'medical',
            'icon': 'fa-solid fa-heart-pulse',
        },

        'respiratory': {
            'class': 'general',
            'icon': 'fa-solid fa-lungs',
        },
    }

    categories = []

    for category in blog_categories:
        icon_data = category_icons.get(
            category.slug,
            {
                'class': 'general',
                'icon': 'fa-solid fa-file-lines',
            }
        )

        categories.append({
            'name': category.name,
            'slug': category.slug,
            'count': category.count,
            'icon_class': icon_data['class'],
            'icon': icon_data['icon'],
        })

    context = {
        'site_settings': SiteSettings.objects.first(),

        'article': article_data_context,

        'related_articles': related_data,

        'comments': comments,

        'comment_form': ArticleCommentForm(),

        'categories': categories,

    }

    return render(
        request,
        'takweblog.html',
        context,
    )


@login_required
@require_POST
def add_article_comment(
    request,
    article_id,
):

    article = get_object_or_404(
        Article,
        id=article_id,
        is_published=True,
    )

    form = ArticleCommentForm(
        request.POST
    )

    if not form.is_valid():

        return JsonResponse(
            {
                'success': False,
                'message': (
                    'متن نظر صحیح نیست.'
                ),
                'errors': form.errors,
            },
            status=400,
        )

    comment = form.save(
        commit=False
    )

    comment.article = article

    comment.user = request.user

    comment.is_approved = False

    comment.save()

    return JsonResponse(
        {
            'success': True,
            'message': (
                'نظر شما ثبت شد و '
                'پس از تایید نمایش داده می‌شود.'
            ),
        }
    )