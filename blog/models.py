from django.conf import settings
from django.db import models
from django.utils import timezone


class BlogCategory(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='نام دسته بندی',
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='اسلاگ',
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='کلاس آیکون',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )

    class Meta:
        verbose_name = 'دسته بندی مقاله'
        verbose_name_plural = 'دسته بندی مقالات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نام تگ',
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='اسلاگ',
    )

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='نویسنده',
    )

    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='دسته بندی',
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles',
        verbose_name='برچسب ها',
    )

    title = models.CharField(
        max_length=250,
        verbose_name='عنوان',
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='اسلاگ',
    )

    excerpt = models.TextField(
        blank=True,
        verbose_name='خلاصه مقاله',
    )

    content = models.TextField(
        verbose_name='متن مقاله',
    )

    cover_image = models.ImageField(
        upload_to='blog/articles/',
        blank=True,
        null=True,
        verbose_name='تصویر مقاله',
    )

    alt_text = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='متن جایگزین تصویر',
    )

    read_time = models.PositiveSmallIntegerField(
        default=5,
        verbose_name='زمان مطالعه',
        help_text='بر حسب دقیقه',
    )

    views = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد بازدید',
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name='مقاله ویژه',
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name='منتشر شده',
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ انتشار',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def publish(self):
        self.is_published = True

        if not self.published_at:
            self.published_at = timezone.now()

        self.save(
            update_fields=[
                'is_published',
                'published_at',
                'updated_at',
            ]
        )

    @property
    def category_name(self):
        return self.category.name if self.category else ''

    @property
    def tags_list(self):
        return self.tags.all()


class ArticleComment(models.Model):

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='مقاله',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_comments',
        verbose_name='کاربر',
    )

    body = models.TextField(
        verbose_name='متن نظر',
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name='تایید شده',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'نظر مقاله'
        verbose_name_plural = 'نظرات مقالات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone} - {self.article.title}'