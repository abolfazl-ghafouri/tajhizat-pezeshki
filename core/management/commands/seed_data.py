from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Address, User
from blog.models import Article, ArticleComment, BlogCategory, Tag
from core.models import (
    CompanyStat,
    FAQ,
    NewsletterSubscriber,
    ServiceFeature,
    SiteSettings,
    TeamMember,
)
from orders.models import Cart, CartItem, Coupon, Order, OrderItem
from store.models import (
    Brand,
    Category,
    Favorite,
    Product,
    ProductFAQ,
    ProductImage,
    ProductReview,
)
from support.models import (
    ConsultationRequest,
    ContactMessage,
    Ticket,
)


class Command(BaseCommand):
    help = "Create realistic demo data for the TajhizatPezeshki project."

    def find_image(self, filename):
        image_dir = Path("static") / "images"

        if not image_dir.exists():
            return None

        target = filename.casefold()

        for path in image_dir.iterdir():
            if path.is_file() and path.name.casefold() == target:
                return path

        return None

    def attach_image(self, image_field, filename):
        path = self.find_image(filename)

        if not path:
            self.stdout.write(
                self.style.WARNING(
                    f"Image not found: static/images/{filename}"
                )
            )
            return False

        with path.open("rb") as image_file:
            image_field.save(
                path.name,
                File(image_file),
                save=False,
            )

        return True

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Creating demo data..."
            )
        )

        # -------------------------------------------------
        # SITE SETTINGS
        # -------------------------------------------------

        site_settings, _ = SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "site_name": "AZARYAZDAN",
                "slogan": "تجهیزات پزشکی و دندانپزشکی",
                "phone": "021-12345678",
                "email": "info@azaryazdan.ir",
                "address": "تهران، خیابان ولیعصر، مرکز تجهیزات پزشکی",
                "working_hours": "شنبه تا پنجشنبه - ۹ تا ۱۸",
                "about_text": (
                    "ارائه دهنده تجهیزات پزشکی و دندانپزشکی "
                    "از برندهای معتبر با تمرکز بر کیفیت، "
                    "مشاوره و خدمات پس از فروش."
                ),
            },
        )

        # -------------------------------------------------
        # CATEGORIES
        # -------------------------------------------------

        categories_data = [
            ("تجهیزات دندانپزشکی", "dental", "fas fa-tooth", "tak1.jpeg"),
            ("تجهیزات پزشکی", "medical", "fas fa-heartbeat", "tak2.jpeg"),
            ("تجهیزات آزمایشگاهی", "laboratory", "fas fa-flask", "tak3.jpeg"),
            ("تجهیزات تصویربرداری", "imaging", "fas fa-x-ray", "tak4.jpeg"),
            ("تجهیزات استریل", "sterilization", "fas fa-syringe", "tak5.jpeg"),
            ("تجهیزات مصرفی", "consumables", "fas fa-box-open", "tak1.jpeg"),
        ]

        categories = {}

        for name, slug, icon, image_name in categories_data:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "icon": icon,
                    "is_active": True,
                },
            )

            if not category.image:
                self.attach_image(category.image, image_name)
                category.save(update_fields=["image"])

            categories[slug] = category

        # -------------------------------------------------
        # BRANDS
        # -------------------------------------------------

        brands_data = [
            ("NSK", "nsk", "brand1.jpeg"),
            ("Woodpecker", "woodpecker", "brand2.jpeg"),
            ("Planmeca", "planmeca", "brand3.jpeg"),
            ("Mindray", "mindray", "brand4.jpeg"),
            ("Dräger", "drager", "brand5.jpeg"),
            ("Saeyang", "saeyang", "brand6.jpeg"),
        ]

        brands = {}

        for name, slug, image_name in brands_data:
            brand, _ = Brand.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "is_active": True,
                },
            )

            if not brand.image:
                self.attach_image(brand, image_name)
                brand.save(update_fields=["image"])

            brands[slug] = brand

        # -------------------------------------------------
        # PRODUCTS
        # -------------------------------------------------

        products_data = [
            {
                "sku": "AZ-DEN-001",
                "slug": "dental-unit-s300",
                "title": "یونیت دندانپزشکی S300",
                "category": "dental",
                "brand": "woodpecker",
                "price": 185000000,
                "discount_price": 169000000,
                "stock": 8,
                "badge": "پرفروش",
                "image": "dandanmiz.jpeg",
                "description": (
                    "یونیت دندانپزشکی S300 با طراحی ارگونومیک، "
                    "صندلی برقی، چراغ LED و کنترل دیجیتال برای "
                    "استفاده حرفه‌ای در مطب و کلینیک."
                ),
                "short_description": "یونیت حرفه‌ای دندانپزشکی با امکانات کامل",
                "warranty_text": "۱۸ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("نوع یونیت", "یونیت دندانپزشکی دیجیتال"),
                    ("چراغ", "LED بدون سایه"),
                    ("کنترل", "پنل لمسی"),
                ],
            },
            {
                "sku": "AZ-STE-001",
                "slug": "class-b-autoclave-23l",
                "title": "اتوکلاو کلاس B 23 لیتری",
                "category": "sterilization",
                "brand": "woodpecker",
                "price": 72000000,
                "discount_price": 68000000,
                "stock": 12,
                "badge": "پیشنهادی",
                "image": "otocluve.jpeg",
                "description": (
                    "اتوکلاو کلاس B با ظرفیت ۲۳ لیتر، مناسب "
                    "مطب‌های دندانپزشکی، کلینیک‌ها و مراکز درمانی."
                ),
                "short_description": "اتوکلاو کلاس B مناسب مطب و کلینیک",
                "warranty_text": "۱۲ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("ظرفیت", "۲۳ لیتر"),
                    ("کلاس", "B"),
                    ("نوع پمپ", "وکیوم"),
                ],
            },
            {
                "sku": "AZ-MED-001",
                "slug": "surgical-suction",
                "title": "ساکشن جراحی",
                "category": "medical",
                "brand": "mindray",
                "price": 28500000,
                "discount_price": None,
                "stock": 20,
                "badge": "جدید",
                "image": "suctiondastgah.jpeg",
                "description": (
                    "دستگاه ساکشن جراحی با قدرت مکش مناسب برای "
                    "اتاق عمل، اورژانس و مراکز درمانی."
                ),
                "short_description": "ساکشن قدرتمند برای محیط‌های درمانی",
                "warranty_text": "۱۲ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("نوع", "ساکشن جراحی"),
                    ("کاربری", "بیمارستان و کلینیک"),
                    ("مخزن", "قابل شستشو"),
                ],
            },
            {
                "sku": "AZ-CAR-001",
                "slug": "three-channel-ecg",
                "title": "دستگاه ECG سه کاناله",
                "category": "medical",
                "brand": "mindray",
                "price": 43500000,
                "discount_price": 39900000,
                "stock": 14,
                "badge": "",
                "image": "dastgahECG.jpeg",
                "description": (
                    "الکتروکاردیوگراف سه کاناله برای ثبت و بررسی "
                    "سیگنال‌های قلبی در مراکز درمانی."
                ),
                "short_description": "ECG سه کاناله با نمایشگر دیجیتال",
                "warranty_text": "۱۸ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("کانال", "۳ کاناله"),
                    ("نمایشگر", "LCD"),
                    ("چاپگر", "حرارتی"),
                ],
            },
            {
                "sku": "AZ-DEN-002",
                "slug": "dental-microscope",
                "title": "میکروسکوپ دندانپزشکی",
                "category": "dental",
                "brand": "nsk",
                "price": 98000000,
                "discount_price": None,
                "stock": 5,
                "badge": "حرفه‌ای",
                "image": "mikroskop dandani.jpeg",
                "description": (
                    "میکروسکوپ دندانپزشکی با بزرگنمایی چندمرحله‌ای "
                    "برای درمان‌های تخصصی و اندودانتیکس."
                ),
                "short_description": "میکروسکوپ تخصصی برای درمان‌های دقیق",
                "warranty_text": "۱۲ ماه گارانتی",
                "featured": False,
                "specs": [
                    ("بزرگنمایی", "۵ تا ۲۵ برابر"),
                    ("نور", "LED"),
                    ("کاربری", "اندودانتیکس و جراحی"),
                ],
            },
            {
                "sku": "AZ-MED-002",
                "slug": "portable-suction",
                "title": "ساکشن پرتابل",
                "category": "medical",
                "brand": "drager",
                "price": 18500000,
                "discount_price": 16900000,
                "stock": 25,
                "badge": "اقتصادی",
                "image": "suction purtabl.jpeg",
                "description": (
                    "ساکشن سبک و قابل حمل برای استفاده در آمبولانس، "
                    "مطب و شرایط اورژانسی."
                ),
                "short_description": "ساکشن سبک و قابل حمل",
                "warranty_text": "۱۲ ماه گارانتی",
                "featured": False,
                "specs": [
                    ("نوع", "پرتابل"),
                    ("منبع تغذیه", "برق شهری"),
                    ("کاربری", "اورژانس"),
                ],
            },
            {
                "sku": "AZ-IMG-001",
                "slug": "digital-xray",
                "title": "سیستم رادیوگرافی دیجیتال",
                "category": "imaging",
                "brand": "planmeca",
                "price": 340000000,
                "discount_price": 319000000,
                "stock": 3,
                "badge": "ویژه",
                "image": "radiyography.jpeg",
                "description": (
                    "سیستم تصویربرداری دیجیتال برای مراکز تشخیصی "
                    "با کیفیت تصویر بالا و گردش کار سریع."
                ),
                "short_description": "سیستم رادیوگرافی دیجیتال حرفه‌ای",
                "warranty_text": "۲۴ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("نوع", "دیجیتال"),
                    ("کاربری", "تصویربرداری پزشکی"),
                    ("خروجی", "تصویر دیجیتال"),
                ],
            },
            {
                "sku": "AZ-LAB-001",
                "slug": "laboratory-centrifuge",
                "title": "سانتریفیوژ آزمایشگاهی",
                "category": "laboratory",
                "brand": "mindray",
                "price": 42000000,
                "discount_price": None,
                "stock": 9,
                "badge": "",
                "image": "santerfiyuzh.jpeg",
                "description": (
                    "سانتریفیوژ آزمایشگاهی مناسب آزمایشگاه‌های "
                    "تشخیص طبی و مراکز تحقیقاتی."
                ),
                "short_description": "سانتریفیوژ رومیزی آزمایشگاهی",
                "warranty_text": "۱۲ ماه گارانتی",
                "featured": False,
                "specs": [
                    ("نوع", "رومیزی"),
                    ("کنترل", "دیجیتال"),
                    ("کاربری", "آزمایشگاهی"),
                ],
            },
            {
                "sku": "AZ-RES-001",
                "slug": "patient-monitor",
                "title": "مانیتور علائم حیاتی",
                "category": "medical",
                "brand": "mindray",
                "price": 78500000,
                "discount_price": 73900000,
                "stock": 7,
                "badge": "محبوب",
                "image": "alaeme hayati.jpeg",
                "description": (
                    "مانیتور علائم حیاتی برای اندازه‌گیری پارامترهای "
                    "اصلی بیمار در بخش‌ها و مراکز درمانی."
                ),
                "short_description": "مانیتور حرفه‌ای علائم حیاتی بیمار",
                "warranty_text": "۱۸ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("پارامترها", "ECG / SpO2 / NIBP"),
                    ("نمایشگر", "LCD رنگی"),
                    ("کاربری", "بخش و ICU"),
                ],
            },
            {
                "sku": "AZ-RES-002",
                "slug": "icu-ventilator",
                "title": "ونتیلاتور ICU",
                "category": "medical",
                "brand": "drager",
                "price": 560000000,
                "discount_price": None,
                "stock": 2,
                "badge": "تخصصی",
                "image": "vantilator.jpeg",
                "description": (
                    "ونتیلاتور تخصصی برای مراقبت‌های ویژه و "
                    "پشتیبانی تنفسی بیماران."
                ),
                "short_description": "ونتیلاتور تخصصی بخش مراقبت‌های ویژه",
                "warranty_text": "۲۴ ماه گارانتی",
                "featured": True,
                "specs": [
                    ("کاربری", "ICU"),
                    ("حالت‌ها", "کنترلی و حمایتی"),
                    ("نمایشگر", "تمام رنگی"),
                ],
            },
            {
                "sku": "AZ-DEN-003",
                "slug": "led-dental-lamp",
                "title": "چراغ LED دندانپزشکی",
                "category": "dental",
                "brand": "saeyang",
                "price": 23500000,
                "discount_price": 21900000,
                "stock": 18,
                "badge": "اقتصادی",
                "image": "cheraghled.jpeg",
                "description": (
                    "چراغ LED دندانپزشکی با نور یکنواخت و "
                    "بدون سایه برای استفاده روزمره در مطب."
                ),
                "short_description": "چراغ LED حرفه‌ای و کم‌مصرف",
                "warranty_text": "۱۲ ماه گارانتی",
                "featured": False,
                "specs": [
                    ("نوع نور", "LED"),
                    ("شدت نور", "قابل تنظیم"),
                    ("کاربری", "مطب دندانپزشکی"),
                ],
            },
        ]

        products = {}

        for data in products_data:
            product, _ = Product.objects.update_or_create(
                sku=data["sku"],
                defaults={
                    "title": data["title"],
                    "slug": data["slug"],
                    "category": categories[data["category"]],
                    "brand": brands[data["brand"]],
                    "short_description": data["short_description"],
                    "description": data["description"],
                    "price": data["price"],
                    "discount_price": data["discount_price"],
                    "stock": data["stock"],
                    "warranty_text": data["warranty_text"],
                    "badge": data["badge"],
                    "is_featured": data["featured"],
                    "is_active": True,
                },
            )

            if not product.main_image:
                self.attach_image(product.main_image, data["image"])
                product.save(update_fields=["main_image"])

            product.specifications.all().delete()
            for order, (name, value) in enumerate(
                data["specs"],
                start=1,
            ):
                ProductSpecification.objects.create(
                    product=product,
                    name=name,
                    value=value,
                    order=order,
                )

            ProductFAQ.objects.filter(
                product=product
            ).delete()

            ProductFAQ.objects.create(
                product=product,
                question=f"آیا {product.title} گارانتی دارد؟",
                answer=product.warranty_text or "دارای گارانتی معتبر است.",
                order=1,
                is_active=True,
            )

            ProductFAQ.objects.create(
                product=product,
                question="آیا امکان مشاوره قبل از خرید وجود دارد؟",
                answer="بله، برای انتخاب مدل مناسب می‌توانید درخواست مشاوره ثبت کنید.",
                order=2,
                is_active=True,
            )

            ProductImage.objects.filter(
                product=product
            ).delete()

            gallery_candidates = [
                data["image"],
                "takmahsulasli.jpeg",
                "main-img.jpeg",
            ]

            seen = set()

            for order, image_name in enumerate(
                gallery_candidates,
                start=1,
            ):
                path = self.find_image(image_name)

                if not path or image_name.casefold() in seen:
                    continue

                gallery = ProductImage(
                    product=product,
                    alt_text=product.title,
                    order=order,
                )

                with path.open("rb") as image_file:
                    gallery.image.save(
                        path.name,
                        File(image_file),
                        save=True,
                    )

                seen.add(image_name.casefold())

            products[data["slug"]] = product

        # -------------------------------------------------
        # BLOG CATEGORIES
        # -------------------------------------------------

        blog_categories_data = [
            ("تجهیزات تصویربرداری", "imaging"),
            ("تجهیزات اتاق عمل", "operating-room"),
            ("مانیتورینگ بیمار", "patient-monitoring"),
            ("تجهیزات تنفسی", "respiratory"),
            ("تجهیزات آزمایشگاهی", "lab"),
            ("تجهیزات دندانپزشکی", "dental"),
        ]

        blog_categories = {}

        for name, slug in blog_categories_data:
            category, _ = BlogCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "is_active": True,
                },
            )

            blog_categories[slug] = category

        # -------------------------------------------------
        # TAGS
        # -------------------------------------------------

        tags_data = [
            ("MRI", "mri"),
            ("اتوکلاو", "autoclave"),
            ("ونتیلاتور", "ventilator"),
            ("ECG", "ecg"),
            ("یونیت دندانپزشکی", "dental-unit"),
            ("تجهیزات پزشکی", "medical-equipment"),
            ("خرید تجهیزات", "equipment-shopping"),
            ("تجهیزات مطب", "clinic-equipment"),
        ]

        tags = {}

        for name, slug in tags_data:
            tag, _ = Tag.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                },
            )

            tags[slug] = tag

        # -------------------------------------------------
        # DEMO CUSTOMER
        # -------------------------------------------------

        demo_user, _ = User.objects.get_or_create(
            phone="09120000001",
            defaults={
                "full_name": "کاربر آزمایشی",
                "email": "demo@example.com",
                "is_active": True,
            },
        )

        if not demo_user.full_name:
            demo_user.full_name = "کاربر آزمایشی"

        demo_user.email = "demo@example.com"
        demo_user.set_unusable_password()
        demo_user.save()

        # -------------------------------------------------
        # ARTICLES
        # -------------------------------------------------

        articles_data = [
            {
                "slug": "how-to-choose-dental-unit",
                "title": "راهنمای خرید یونیت دندانپزشکی؛ نکات مهم قبل از خرید",
                "category": "dental",
                "image": "takweblog.jpeg",
                "excerpt": "مهم‌ترین معیارهای انتخاب یونیت دندانپزشکی برای مطب و کلینیک.",
                "read_time": 6,
                "views": 4200,
                "featured": True,
                "tags": ["dental-unit", "equipment-shopping", "clinic-equipment"],
                "content": (
                    "یونیت دندانپزشکی یکی از مهم‌ترین تجهیزات هر مطب است. "
                    "در زمان خرید باید ارگونومی، امکانات جانبی، خدمات پس از فروش "
                    "و کیفیت ساخت را در کنار بودجه بررسی کنید."
                ),
            },
            {
                "slug": "mri-vs-ct-scan",
                "title": "تفاوت‌های کلیدی MRI و CT Scan در تشخیص پزشکی",
                "category": "imaging",
                "image": "mri jadid.jpeg",
                "excerpt": "آشنایی با تفاوت کاربرد، مزایا و محدودیت‌های MRI و CT Scan.",
                "read_time": 7,
                "views": 3600,
                "featured": True,
                "tags": ["mri", "medical-equipment"],
                "content": (
                    "MRI و CT هر دو از ابزارهای مهم تصویربرداری پزشکی هستند، "
                    "اما فناوری، کاربرد و شرایط استفاده از آن‌ها متفاوت است."
                ),
            },
            {
                "slug": "class-b-vs-class-s-autoclave",
                "title": "اتوکلاو بیمارستانی: مقایسه کلاس B و کلاس S",
                "category": "operating-room",
                "image": "otocluve.jpeg",
                "excerpt": "کلاس B و S چه تفاوتی دارند و برای چه محیطی مناسب هستند؟",
                "read_time": 5,
                "views": 2900,
                "featured": False,
                "tags": ["autoclave", "medical-equipment"],
                "content": (
                    "برای انتخاب اتوکلاو باید نوع ابزار، حجم استفاده و نیازهای "
                    "استریل‌سازی مرکز درمانی را در نظر گرفت."
                ),
            },
            {
                "slug": "ventilator-buying-guide",
                "title": "راهنمای انتخاب دستگاه ونتیلاتور برای بیمارستان‌ها",
                "category": "respiratory",
                "image": "vantilator.jpeg",
                "excerpt": "معیارهای مهم انتخاب ونتیلاتور مناسب برای مراکز درمانی.",
                "read_time": 8,
                "views": 5100,
                "featured": True,
                "tags": ["ventilator", "medical-equipment"],
                "content": (
                    "انتخاب ونتیلاتور به شرایط مرکز درمانی، نوع بیماران، "
                    "مدهای تنفسی و خدمات پس از فروش وابسته است."
                ),
            },
            {
                "slug": "medical-equipment-preventive-maintenance",
                "title": "نگهداری پیشگیرانه تجهیزات پزشکی",
                "category": "patient-monitoring",
                "image": "dastgahECG.jpeg",
                "excerpt": "چطور با نگهداری منظم، هزینه خرابی تجهیزات را کاهش دهیم.",
                "read_time": 5,
                "views": 2400,
                "featured": False,
                "tags": ["medical-equipment"],
                "content": (
                    "نگهداری پیشگیرانه شامل بررسی دوره‌ای، ثبت خرابی‌ها، "
                    "تمیزکاری و سرویس تجهیزات بر اساس برنامه مشخص است."
                ),
            },
            {
                "slug": "patient-monitoring-basics",
                "title": "مبانی انتخاب مانیتورینگ بیمار",
                "category": "patient-monitoring",
                "image": "alaeme hayati.jpeg",
                "excerpt": "پارامترهای اصلی مانیتورینگ و نکات انتخاب دستگاه.",
                "read_time": 4,
                "views": 1800,
                "featured": False,
                "tags": ["medical-equipment", "ecg"],
                "content": (
                    "برای انتخاب مانیتور بیمار ابتدا باید پارامترهای مورد نیاز "
                    "مرکز درمانی را مشخص و سپس مدل مناسب را مقایسه کرد."
                ),
            },
            {
                "slug": "ecg-three-channel-guide",
                "title": "آشنایی با دستگاه ECG سه کاناله",
                "category": "patient-monitoring",
                "image": "magale1.jpeg",
                "excerpt": "نگاهی ساده به کاربردها و ویژگی‌های ECG سه کاناله.",
                "read_time": 4,
                "views": 1500,
                "featured": False,
                "tags": ["ecg", "medical-equipment"],
                "content": (
                    "ECG سه کاناله برای ثبت سیگنال‌های قلبی و بررسی اولیه "
                    "وضعیت الکتریکی قلب در مراکز درمانی استفاده می‌شود."
                ),
            },
            {
                "slug": "dental-unit-maintenance",
                "title": "نکات نگهداری یونیت دندانپزشکی",
                "category": "dental",
                "image": "magale2.jpeg",
                "excerpt": "چگونه عمر مفید یونیت دندانپزشکی را افزایش دهیم.",
                "read_time": 5,
                "views": 2100,
                "featured": False,
                "tags": ["dental-unit", "clinic-equipment"],
                "content": (
                    "سرویس دوره‌ای، نظافت مسیرهای آب و هوا و استفاده صحیح "
                    "از ابزارها به افزایش عمر یونیت کمک می‌کند."
                ),
            },
        ]

        articles = {}

        for data in articles_data:
            article, _ = Article.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "author": demo_user,
                    "category": blog_categories[data["category"]],
                    "title": data["title"],
                    "excerpt": data["excerpt"],
                    "content": data["content"],
                    "read_time": data["read_time"],
                    "views": data["views"],
                    "is_featured": data["featured"],
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )

            if not article.cover_image:
                self.attach_image(
                    article.cover_image,
                    data["image"],
                )
                article.save(update_fields=["cover_image"])

            article.tags.set(
                [tags[tag_slug] for tag_slug in data["tags"]]
            )

            articles[data["slug"]] = article

        # -------------------------------------------------
        # PRODUCT REVIEWS
        # -------------------------------------------------

        review_data = [
            (
                "dental-unit-s300",
                5,
                "طراحی و امکانات دستگاه برای مطب خیلی مناسب است.",
            ),
            (
                "class-b-autoclave-23l",
                4,
                "ظرفیت مناسب و استفاده از آن ساده است.",
            ),
            (
                "patient-monitor",
                5,
                "نمایشگر خوب و رابط کاربری ساده‌ای دارد.",
            ),
        ]

        for slug, rating, body in review_data:
            product = products[slug]

            ProductReview.objects.get_or_create(
                product=product,
                user=demo_user,
                body=body,
                defaults={
                    "rating": rating,
                    "is_approved": True,
                },
            )

        # -------------------------------------------------
        # FAVORITES
        # -------------------------------------------------

        Favorite.objects.get_or_create(
            user=demo_user,
            product=products["dental-unit-s300"],
        )

        Favorite.objects.get_or_create(
            user=demo_user,
            product=products["patient-monitor"],
        )

        # -------------------------------------------------
        # ADDRESS
        # -------------------------------------------------

        Address.objects.update_or_create(
            user=demo_user,
            title="آدرس اصلی",
            defaults={
                "recipient_name": demo_user.full_name,
                "phone": demo_user.phone,
                "province": "تهران",
                "city": "تهران",
                "address": "خیابان ولیعصر، کوچه نمونه، پلاک ۱۰",
                "postal_code": "1234567890",
                "is_default": True,
            },
        )

        # -------------------------------------------------
        # CART
        # -------------------------------------------------

        cart, _ = Cart.objects.get_or_create(
            user=demo_user
        )

        CartItem.objects.update_or_create(
            cart=cart,
            product=products["dental-unit-s300"],
            defaults={
                "quantity": 1,
            },
        )

        # -------------------------------------------------
        # COUPON
        # -------------------------------------------------

        Coupon.objects.update_or_create(
            code="AZAR10",
            defaults={
                "discount_percent": 10,
                "is_active": True,
                "expires_at": None,
            },
        )

        # -------------------------------------------------
        # SAMPLE ORDER
        # -------------------------------------------------

        order, _ = Order.objects.update_or_create(
            number="ORD-DEMO-0001",
            defaults={
                "user": demo_user,
                "status": Order.STATUS_SHIPPING,
                "total_amount": 203500000,
                "discount_amount": 20350000,
                "final_amount": 183150000,
                "recipient_name": demo_user.full_name,
                "phone": demo_user.phone,
                "province": "تهران",
                "city": "تهران",
                "address": "خیابان ولیعصر، کوچه نمونه، پلاک ۱۰",
                "postal_code": "1234567890",
            },
        )

        OrderItem.objects.filter(order=order).delete()

        OrderItem.objects.create(
            order=order,
            product=products["dental-unit-s300"],
            product_title=products["dental-unit-s300"].title,
            sku=products["dental-unit-s300"].sku,
            unit_price=169000000,
            quantity=1,
            total_price=169000000,
        )

        OrderItem.objects.create(
            order=order,
            product=products["class-b-autoclave-23l"],
            product_title=products["class-b-autoclave-23l"].title,
            sku=products["class-b-autoclave-23l"].sku,
            unit_price=34000000,
            quantity=1,
            total_price=34000000,
        )

        # -------------------------------------------------
        # SUPPORT
        # -------------------------------------------------

        Ticket.objects.update_or_create(
            number="TKT-000001",
            defaults={
                "user": demo_user,
                "subject": "درخواست مشاوره درباره یونیت",
                "message": "برای انتخاب یونیت مناسب یک کلینیک کوچک راهنمایی می‌خواهم.",
                "category": "مشاوره خرید",
                "priority": Ticket.PRIORITY_NORMAL,
                "status": Ticket.STATUS_OPEN,
                "related_product": products["dental-unit-s300"],
            },
        )

        ContactMessage.objects.get_or_create(
            email="demo@example.com",
            subject="سوال درباره محصولات",
            defaults={
                "user": demo_user,
                "name": demo_user.full_name,
                "phone": demo_user.phone,
                "message": "نمونه پیام برای نمایش پنل مدیریت.",
                "status": ContactMessage.STATUS_NEW,
            },
        )

        ConsultationRequest.objects.get_or_create(
            phone=demo_user.phone,
            product=products["dental-unit-s300"],
            defaults={
                "user": demo_user,
                "name": demo_user.full_name,
                "email": demo_user.email,
                "message": "درخواست مشاوره قبل از خرید.",
                "status": ConsultationRequest.STATUS_NEW,
            },
        )

        # -------------------------------------------------
        # CORE CONTENT
        # -------------------------------------------------

        service_features = [
            (
                "fas fa-truck",
                "ارسال به سراسر کشور",
                "ارسال سریع تجهیزات به مراکز درمانی",
            ),
            (
                "fas fa-headset",
                "مشاوره تخصصی",
                "کمک به انتخاب محصول مناسب",
            ),
            (
                "fas fa-tools",
                "خدمات پس از فروش",
                "پشتیبانی و سرویس تجهیزات",
            ),
            (
                "fas fa-user-graduate",
                "آموزش و نصب",
                "آموزش کامل و نصب تجهیزات",
            ),
        ]

        for order, (icon, title, description) in enumerate(
            service_features,
            start=1,
        ):
            ServiceFeature.objects.update_or_create(
                order=order,
                defaults={
                    "icon": icon,
                    "title": title,
                    "description": description,
                    "is_active": True,
                },
            )

        stats = [
            ("fas fa-calendar", "۱۵+", "سال تجربه"),
            ("fas fa-box", "۵۰۰+", "محصول"),
            ("fas fa-hospital", "۲۰۰+", "مشتری"),
            ("fas fa-headset", "۲۴/۷", "پشتیبانی"),
        ]

        for order, (icon, value, label) in enumerate(
            stats,
            start=1,
        ):
            CompanyStat.objects.update_or_create(
                order=order,
                defaults={
                    "icon": icon,
                    "value": value,
                    "label": label,
                    "is_active": True,
                },
            )

        team = [
            ("دکتر علی رضایی", "مدیر فنی"),
            ("مهندس سارا محمدی", "کارشناس تجهیزات پزشکی"),
            ("مهندس مهدی کریمی", "کارشناس تجهیزات دندانپزشکی"),
        ]

        for order, (name, role) in enumerate(team, start=1):
            TeamMember.objects.update_or_create(
                name=name,
                defaults={
                    "role": role,
                    "is_active": True,
                    "order": order,
                },
            )

        faq_data = [
            (
                "چطور محصول مناسب را انتخاب کنم؟",
                "از طریق بخش مشاوره می‌توانید مشخصات نیاز خود را ارسال کنید تا راهنمایی شوید.",
            ),
            (
                "آیا محصولات دارای گارانتی هستند؟",
                "مدت گارانتی هر محصول در صفحه همان محصول درج شده است.",
            ),
            (
                "آیا به سراسر کشور ارسال دارید؟",
                "بله، سفارش‌ها به سراسر کشور ارسال می‌شوند.",
            ),
            (
                "چطور سفارش خود را پیگیری کنم؟",
                "از بخش داشبورد مشتری می‌توانید سفارش‌های خود را مشاهده کنید.",
            ),
        ]

        for order, (question, answer) in enumerate(
            faq_data,
            start=1,
        ):
            FAQ.objects.update_or_create(
                question=question,
                defaults={
                    "answer": answer,
                    "order": order,
                    "is_active": True,
                },
            )

        newsletter, _ = NewsletterSubscriber.objects.update_or_create(
            email="demo@example.com",
            defaults={
                "is_active": True,
            },
        )

        # -------------------------------------------------
        # FINAL OUTPUT
        # -------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data created successfully."
            )
        )

        self.stdout.write(
            f"Products: {Product.objects.count()}"
        )
        self.stdout.write(
            f"Categories: {Category.objects.count()}"
        )
        self.stdout.write(
            f"Brands: {Brand.objects.count()}"
        )
        self.stdout.write(
            f"Articles: {Article.objects.count()}"
        )
        self.stdout.write(
            f"Users: {User.objects.count()}"
        )
        self.stdout.write(
            f"Orders: {Order.objects.count()}"
        )
        self.stdout.write(
            f"Tickets: {Ticket.objects.count()}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.NOTICE(
                "Demo customer:"
            )
        )
        self.stdout.write(
            "Phone: 09120000001"
        )
        self.stdout.write(
            "Login with OTP; the OTP will be printed in the terminal."
        )
        self.stdout.write("")
        self.stdout.write(
            "Coupon: AZAR10"
        )
