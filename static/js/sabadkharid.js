document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const loginUrl = body.dataset.loginUrl || '/accounts/login/';
    const orderSuccess = body.dataset.orderSuccess === '1';

    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');

    hamburger?.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu?.classList.toggle('active');
    });

    navMenu?.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger?.classList.remove('active');
            navMenu?.classList.remove('active');
        });
    });

    document.querySelectorAll('[data-navigation-url]').forEach(icon => {
        const go = () => {
            if (icon.dataset.navigationUrl) {
                window.location.href = icon.dataset.navigationUrl;
            }
        };

        icon.addEventListener('click', go);
        icon.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                go();
            }
        });
    });

    const csrf = () => document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    )?.value || '';

    const post = (url, data = {}) => {
        const form = new FormData();
        form.set('csrfmiddlewaretoken', csrf());

        Object.entries(data).forEach(([key, value]) => {
            form.set(key, value);
        });

        return fetch(url, {
            method: 'POST',
            body: form,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
    };

    function formatNumber(num) {
        return Number(num || 0).toLocaleString('fa-IR');
    }

    function parseNumber(value) {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    const arabicDigits = '٠١٢٣٤٥٦٧٨٩';

    const normalized = String(value ?? '')
        .replace(/[۰-۹]/g, digit => {
            return persianDigits.indexOf(digit);
        })
        .replace(/[٠-٩]/g, digit => {
            return arabicDigits.indexOf(digit);
        })
        .replace(/٬/g, '')
        .replace(/,/g, '')
        .trim();

    const number = Number(normalized);

    return Number.isFinite(number) ? number : 0;
}

    function updateSummary(summary) {
        if (!summary) return;

        const totalItemsPrice = document.getElementById(
            'totalItemsPrice'
        );
        const totalDiscount = document.getElementById(
            'totalDiscount'
        );
        const finalPrice = document.getElementById(
            'finalPrice'
        );

        if (totalItemsPrice) {
            totalItemsPrice.textContent = (
                summary.items_total_display || '۰ تومان'
            );
        }

        if (totalDiscount) {
            totalDiscount.textContent =
                '− ' + (
                    summary.discount_display || '۰ تومان'
                );
        }

        if (finalPrice) {
            finalPrice.textContent = (
                summary.final_total_display || '۰ تومان'
            );
        }
    }

    function updateCartCount() {
    const items = document.querySelectorAll('.cart-item');

    const count = Array.from(items).reduce(
        (total, item) => {
            const quantity = parseNumber(
                item.querySelector('.qty-display')?.textContent
            );

            return total + quantity;
        },
        0
    );

    const label = document.querySelector(
        '.cart-item-count'
    );

    if (label) {
        label.textContent =
            `${formatNumber(count)} کالا در سبد`;
    }

    const grid = document.getElementById('cartGrid');
    const empty = document.getElementById('emptyCart');
    const title = document.querySelector(
        '.page-title-section'
    );

    if (count === 0) {
        if (grid) grid.style.display = 'none';
        if (empty) empty.style.display = 'block';
        if (title) title.style.display = 'none';
    } else {
        if (grid) grid.style.display = '';
        if (empty) empty.style.display = 'none';
        if (title) title.style.display = '';
    }
}

    async function updateItem(button, change) {
        const item = button.closest('.cart-item');
        if (!item) return;

        const qtyElement = item.querySelector('.qty-display');
        const current = parseNumber(
            qtyElement?.textContent
        ) || 1;
        const quantity = Math.max(1, current + change);
        const url = item.dataset.updateUrl;

        if (!url) return;

        try {
            const response = await post(url, { quantity });

            if (response.redirected) {
                window.location.href = loginUrl;
                return;
            }

            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(
                    data.message ||
                    'تغییر تعداد انجام نشد.'
                );
                return;
            }

            if (qtyElement) {
                qtyElement.textContent = quantity;
            }

            const itemTotal = item.querySelector('.item-total');

            if (itemTotal) {
                itemTotal.textContent = (
                    data.item_total_display || ''
                );
            }

            updateSummary(data.summary);
        } catch (error) {
            console.error(error);
            alert('خطایی در تغییر تعداد رخ داد.');
        }
    }

    async function removeItem(button) {
        const item = button.closest('.cart-item');
        if (!item) return;

        const url = item.dataset.removeUrl;
        if (!url) return;

        try {
            const response = await post(url);

            if (response.redirected) {
                window.location.href = loginUrl;
                return;
            }

            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(
                    data.message ||
                    'حذف انجام نشد.'
                );
                return;
            }

            item.remove();
            updateSummary(data.summary);
            updateCartCount();
        } catch (error) {
            console.error(error);
            alert('خطایی در حذف محصول رخ داد.');
        }
    }

    document.querySelectorAll(
        '[data-cart-action="increase"]'
    ).forEach(button => {
        button.addEventListener(
            'click',
            () => updateItem(button, 1)
        );
    });

    document.querySelectorAll(
        '[data-cart-action="decrease"]'
    ).forEach(button => {
        button.addEventListener(
            'click',
            () => updateItem(button, -1)
        );
    });

    document.querySelectorAll(
        '[data-cart-action="remove"]'
    ).forEach(button => {
        button.addEventListener(
            'click',
            () => removeItem(button)
        );
    });

    const selectAll = document.getElementById('selectAll');

    selectAll?.addEventListener('change', () => {
        document.querySelectorAll('.item-checkbox').forEach(box => {
            box.checked = selectAll.checked;
        });
    });

    const couponInput = document.getElementById('couponInput');
    const couponMessage = document.getElementById('couponMsg');
    const couponCodeDisplay = document.getElementById(
        'couponCodeDisplay'
    );

    const applyCouponButton = document.getElementById(
        'applyCouponBtn'
    );

    applyCouponButton?.addEventListener('click', async () => {
        const code = couponInput?.value.trim();
        const url = applyCouponButton.dataset.couponUrl;

        if (!code || !url) return;

        try {
            const response = await post(url, { code });

            if (response.redirected) {
                window.location.href = loginUrl;
                return;
            }

            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(
                    data.message ||
                    'کد تخفیف معتبر نیست.'
                );
                return;
            }

            couponMessage?.classList.remove('is-hidden');

            if (couponCodeDisplay) {
                couponCodeDisplay.textContent = (
                    data.code || code
                ).toUpperCase();
            }

            if (couponInput) {
                couponInput.value = '';
            }

            updateSummary(data.summary);
        } catch (error) {
            console.error(error);
            alert('خطایی در اعمال کد تخفیف رخ داد.');
        }
    });

    const removeCouponButton = document.getElementById(
        'removeCouponBtn'
    );

    removeCouponButton?.addEventListener('click', async () => {
        const url = removeCouponButton.dataset.removeCouponUrl;
        if (!url) return;

        try {
            const response = await post(url);
            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(
                    data.message ||
                    'حذف کد تخفیف ناموفق بود.'
                );
                return;
            }

            couponMessage?.classList.add('is-hidden');
            updateSummary(data.summary);
        } catch (error) {
            console.error(error);
            alert('خطایی در حذف کد تخفیف رخ داد.');
        }
    });

    const modal = document.getElementById('infoModal');

    function openModal() {
        modal?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal?.classList.remove('active');
        document.body.style.overflow = '';
    }

    document.getElementById('checkoutBtn')?.addEventListener(
        'click',
        () => {
            const items = document.querySelectorAll('.cart-item');

            if (!items.length) {
                alert('سبد خرید خالی است.');
                return;
            }

            const allSelected = Array.from(
                document.querySelectorAll('.item-checkbox')
            ).every(box => box.checked);

            if (!allSelected) {
                alert('برای ادامه فرایند پرداخت، همه کالاها را انتخاب کنید.');
                return;
            }

            openModal();
        }
    );

    document.getElementById(
        'cancelCheckoutBtn'
    )?.addEventListener('click', closeModal);

    modal?.addEventListener('click', event => {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });

    document.querySelectorAll(
        '[data-ajax-form="newsletter"]'
    ).forEach(form => {
        form.addEventListener('submit', async event => {
            event.preventDefault();

            try {
                const response = await fetch(
                    form.action,
                    {
                        method: 'POST',
                        body: new FormData(form),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    }
                );

                const data = await response.json();
                alert(
                    data.message ||
                    'درخواست انجام شد.'
                );

                if (data.success) {
                    form.reset();
                }
            } catch (error) {
                console.error(error);
                alert(
                    'خطایی در عضویت خبرنامه رخ داد.'
                );
            }
        });
    });

    if (orderSuccess) {
        alert('سفارش شما با موفقیت ثبت شد.');
    }

    updateCartCount();
});
