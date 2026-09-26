from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.urls import reverse

from blog.models import Article, BlogCategory
from core.models import CompanyStat, ServiceFeature, SiteSettings
from .forms import ProductReviewForm
from .models import (
    Brand,
    Category,
    Favorite,
    Product,
)


def format_price(price):
    return f'{price:,} تومان'


def get_product_image(product):
    if product.main_image:
        return product.main_image.url

    return static('images/main-img.jpeg')


def product_card_data(product, request=None):
    reviews = product.reviews.filter(
        is_approved=True
    )

    review_count = reviews.count()

    average_rating = (
        reviews.aggregate(
            average=Avg('rating')
        )['average']
        or 0
    )

    is_favorite = False

    if request and request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            product=product,
        ).exists()

    return {
        'id': product.id,
        'title': product.title,
        'brand_name': (
            product.brand.name
            if product.brand
            else ''
        ),
        'brand_slug': (
            product.brand.slug
            if product.brand
            else ''
        ),
        'category_slug': (
            product.category.slug
            if product.category
            else ''
        ),
        'category_name': (
            product.category.name
            if product.category
            else ''
        ),
        'badge': product.badge,
        'rating': round(average_rating, 1),
        'rating_display': f'{average_rating:.1f}',
        'review_count': review_count,
        'price': product.final_price,
        'price_display': format_price(
            product.final_price
        ),
        'image_url': get_product_image(product),
        'image_alt': product.title,
        'detail_url': reverse(
    'product_detail',
        kwargs={
            'slug': product.slug
        }
    ),

    'add_to_cart_url': reverse(
        'add_to_cart',
        kwargs={
            'product_id': product.id
        }
    ),
        'is_favorite': is_favorite,
    }


def home(request):

    site_settings = SiteSettings.objects.first()

    featured_products = (
        Product.objects
        .filter(
            is_active=True,
            is_featured=True,
        )
        .select_related(
            'brand',
            'category',
        )
        .order_by('-created_at')[:8]
    )

    latest_products = (
        Product.objects
        .filter(
            is_active=True,
        )
        .select_related(
            'brand',
            'category',
        )
        .order_by('-created_at')[:8]
    )

    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by('name')
    )

    brands = (
        Brand.objects
        .filter(is_active=True)
        .order_by('name')
    )

    latest_articles = (
        Article.objects
        .filter(is_published=True)
        .select_related(
            'category',
        )
        .order_by('-published_at', '-created_at')[:6]
    )

    service_features = (
        ServiceFeature.objects
        .filter(is_active=True)
        .order_by('order')
    )

    company_stats = (
        CompanyStat.objects
        .filter(is_active=True)
        .order_by('order')
    )

    featured_data = [
        product_card_data(
            product,
            request,
        )
        for product in featured_products
    ]

    latest_data = [
        product_card_data(
            product,
            request,
        )
        for product in latest_products
    ]

    latest_articles_data = []

    for article in latest_articles:

        if article.cover_image:
            image_url = article.cover_image.url
        else:
            image_url = static(
                'images/webloggggg.jpeg'
            )

        latest_articles_data.append({
            'id': article.id,
            'title': article.title,
            'excerpt': article.excerpt,
            'image_url': image_url,
            'image_alt': article.alt_text or article.title,
            'detail_url': f'/blog/{article.slug}/',
        })

    categories_data = []

    for category in categories:

        products = category.products.filter(
            is_active=True
        )[:4]

        categories_data.append({
            'name': category.name,
            'slug': category.slug,
            'icon': category.icon,

            'count': category.products.filter(
                is_active=True
            ).count(),

            'items': [
                product.title
                for product in products
            ],

            'image_url': (
                category.image.url
                if category.image
                else static('images/tak1.jpeg')
            ),

            'image_alt': category.name,

            'url': f'/shop/?category={category.slug}',

            'card_class': '',
        })

    brands_data = []

    for brand in brands:

        brands_data.append({
            'name': brand.name,
            'slug': brand.slug,
            'image_url': (
                brand.image.url
                if brand.image
                else static('images/brand1.jpeg')
            ),
        })

    context = {
        'site_settings': site_settings,
        'featured_products': featured_data,
        'latest_products': latest_data,
        'categories': categories_data,
        'brands': brands_data,
        'latest_articles': latest_articles_data,
        'service_features': service_features,
        'company_stats': company_stats,
        'company_highlights': company_stats[:4],
    }

    return render(
        request,
        'landingg.html',
        context,
    )


def shop(request):

    products = (
        Product.objects
        .filter(
            is_active=True,
        )
        .select_related(
            'brand',
            'category',
        )
        .prefetch_related(
            'reviews',
        )
    )

    # ---------------- SEARCH ----------------

    query = request.GET.get(
        'q',
        ''
    ).strip()

    if query:
        products = products.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(short_description__icontains=query)
        )

    # ---------------- CATEGORY ----------------

    selected_category = request.GET.get(
        'category',
        ''
    ).strip()

    if selected_category:
        products = products.filter(
            category__slug=selected_category
        )

    # ---------------- BRAND ----------------

    selected_brands = request.GET.getlist(
        'brand'
    )

    if selected_brands:
        products = products.filter(
            brand__slug__in=selected_brands
        )

    # ---------------- PRICE ----------------

    min_price = request.GET.get(
        'min_price'
    )

    max_price = request.GET.get(
        'max_price'
    )

    if min_price:

        try:
            min_price = int(min_price)
            products = products.filter(
                price__gte=min_price
            )
        except ValueError:
            min_price = ''

    if max_price:

        try:
            max_price = int(max_price)
            products = products.filter(
                price__lte=max_price
            )
        except ValueError:
            max_price = ''

    # ---------------- STOCK ----------------

    stock = request.GET.get(
        'stock'
    )

    if stock == 'available':
        products = products.filter(
            stock__gt=0
        )

    elif stock == 'unavailable':
        products = products.filter(
            stock=0
        )

    # ---------------- SORT ----------------

    sort = request.GET.get(
        'sort',
        'newest'
    )

    if sort == 'cheap':

        products = products.order_by(
            'price'
        )

    elif sort == 'expensive':

        products = products.order_by(
            '-price'
        )

    elif sort == 'popular':

        products = products.annotate(
            total_reviews=Count(
                'reviews',
                filter=Q(
                    reviews__is_approved=True
                )
            )
        ).order_by(
            '-total_reviews',
            '-created_at',
        )

    else:

        products = products.order_by(
            '-created_at'
        )

    # ---------------- PAGINATION ----------------

    paginator = Paginator(
        products,
        12
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    products_data = [
        product_card_data(
            product,
            request,
        )
        for product in page_obj
    ]

    # ---------------- CATEGORIES ----------------

    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(
            product_count=Count(
                'products',
                filter=Q(
                    products__is_active=True
                )
            )
        )
        .order_by('name')
    )

    categories_data = []

    for category in categories:

        categories_data.append({
            'name': category.name,
            'slug': category.slug,
            'icon': category.icon,
            'count': category.product_count,
            'url': f'/shop/?category={category.slug}',
        })

    # ---------------- BRANDS ----------------

    brands = (
        Brand.objects
        .filter(is_active=True)
        .annotate(
            product_count=Count(
                'products',
                filter=Q(
                    products__is_active=True
                )
            )
        )
        .order_by('name')
    )

    brands_data = []

    for brand in brands:

        brands_data.append({
            'name': brand.name,
            'slug': brand.slug,
            'product_count': brand.product_count,
        })

    context = {
        'site_settings': SiteSettings.objects.first(),

        'products': products_data,

        'categories': categories_data,

        'brands': brands_data,

        'pagination': page_obj,

        'selected_category': selected_category,

        'selected_brands': selected_brands,

        'min_price': min_price or '',

        'max_price': max_price or '',

        'query': query,
    }

    return render(
        request,
        'shop.html',
        context,
    )


def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects
        .select_related(
            'brand',
            'category',
        )
        .prefetch_related(
            'gallery_images',
            'specifications',
            'faqs',
        ),
        slug=slug,
        is_active=True,
    )

    approved_reviews = (
        product.reviews
        .filter(is_approved=True)
        .select_related('user')
        .order_by('-created_at')
    )

    comments = []

    for review in approved_reviews:

        comments.append({
            'id': review.id,
            'user_display': (
                review.user.full_name
                or review.user.phone
            ),
            'rating_stars': review.rating_stars,
            'rating': review.rating,
            'body': review.body,
            'created_at': review.created_at,
        })

    gallery_images = []

    if product.main_image:

        gallery_images.append({
            'url': product.main_image.url,
            'alt': product.title,
        })

    for image in product.gallery_images.all():

        gallery_images.append({
            'url': image.image.url,
            'alt': image.alt_text or product.title,
        })

    related_products = (
        Product.objects
        .filter(
            is_active=True,
            category=product.category,
        )
        .exclude(
            id=product.id
        )
        .select_related(
            'brand',
            'category',
        )
        .order_by('-created_at')[:4]
    )

    related_data = [
        product_card_data(
            item,
            request,
        )
        for item in related_products
    ]

    product_data = {
        'id': product.id,
        'title': product.title,
        'slug': product.slug,
        'brand_name': (
            product.brand.name
            if product.brand
            else ''
        ),
        'category_name': (
            product.category.name
            if product.category
            else ''
        ),
        'price': product.final_price,
        'price_display': format_price(
            product.final_price
        ),
        'description': product.description,
        'short_description': product.short_description,
        'warranty_text': product.warranty_text,
        'badge': product.badge,
        'image_url': get_product_image(product),
        'image_alt': product.title,
        'gallery_images': gallery_images,
        'specifications': product.specifications.all(),
    }

    context = {
        'site_settings': SiteSettings.objects.first(),

        'product': product_data,

        'comments': comments,

        'faqs': product.faqs.filter(
            is_active=True
        ),

        'related_products': related_data,

        'review_form': ProductReviewForm(),

        'is_favorite': (
            Favorite.objects.filter(
                user=request.user,
                product=product,
            ).exists()
            if request.user.is_authenticated
            else False
        ),
    }

    return render(
        request,
        'tkmhsul.html',
        context,
    )


@login_required
@require_POST
def toggle_favorite(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    favorite = Favorite.objects.filter(
        user=request.user,
        product=product,
    ).first()

    if favorite:

        favorite.delete()

        return JsonResponse({
            'success': True,
            'is_favorite': False,
            'message': 'از علاقه مندی ها حذف شد.',
        })

    Favorite.objects.create(
        user=request.user,
        product=product,
    )

    return JsonResponse({
        'success': True,
        'is_favorite': True,
        'message': 'به علاقه مندی ها اضافه شد.',
    })


@login_required
@require_POST
def add_product_review(
    request,
    product_id,
):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    form = ProductReviewForm(
        request.POST
    )

    if not form.is_valid():

        return JsonResponse({
            'success': False,
            'message': 'اطلاعات نظر صحیح نیست.',
            'errors': form.errors,
        }, status=400)

    review = form.save(
        commit=False
    )

    review.user = request.user
    review.product = product
    review.is_approved = False

    review.save()

    return JsonResponse({
        'success': True,
        'message': 'نظر شما ثبت شد و پس از تایید نمایش داده می‌شود.',
    })