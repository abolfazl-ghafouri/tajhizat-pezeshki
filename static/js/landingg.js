document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const loginUrl = body.dataset.loginUrl || '/accounts/login/';
    const isAuthenticated = body.dataset.isAuthenticated === '1';

    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    document.querySelectorAll('[data-navigation-url]').forEach(element => {
        const go = () => {
            if (element.dataset.navigationUrl) {
                window.location.href = element.dataset.navigationUrl;
            }
        };

        element.addEventListener('click', go);
        element.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                go();
            }
        });
    });

    const slider = document.getElementById('slider');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');

    if (slider && nextBtn && prevBtn) {
        nextBtn.addEventListener('click', () => {
            slider.scrollBy({
                left: -slider.clientWidth,
                behavior: 'smooth'
            });
        });

        prevBtn.addEventListener('click', () => {
            slider.scrollBy({
                left: slider.clientWidth,
                behavior: 'smooth'
            });
        });
    }

    const specialSlider = document.getElementById('specialSlider');
    const specialPrev = document.getElementById('specialPrev');
    const specialNext = document.getElementById('specialNext');

    if (specialSlider && specialPrev && specialNext) {
        specialNext.addEventListener('click', () => {
            specialSlider.scrollBy({
                left: -300,
                behavior: 'smooth'
            });
        });

        specialPrev.addEventListener('click', () => {
            specialSlider.scrollBy({
                left: 300,
                behavior: 'smooth'
            });
        });
    }

    function getCSRFToken() {
        return document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
        )?.value || '';
    }

    async function post(url, data = {}) {
        const formData = new FormData();
        formData.set(
            'csrfmiddlewaretoken',
            getCSRFToken()
        );

        Object.entries(data).forEach(([key, value]) => {
            formData.set(key, value);
        });

        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
    }

    document.querySelectorAll(
        '[data-product-action="quick-view"]'
    ).forEach(button => {
        button.addEventListener('click', () => {
            const url = button.dataset.productDetailUrl;

            if (url) {
                window.location.href = url;
            }
        });
    });

    document.querySelectorAll(
        '[data-product-action="cart"][data-cart-url]'
    ).forEach(button => {
        button.addEventListener('click', async () => {
            if (!isAuthenticated) {
                window.location.href = loginUrl;
                return;
            }

            try {
                const response = await post(
                    button.dataset.cartUrl
                );

                if (response.redirected) {
                    window.location.href = loginUrl;
                    return;
                }

                const data = await response.json();

                if (!response.ok || !data.success) {
                    alert(
                        data.message ||
                        'خطا در افزودن محصول.'
                    );
                    return;
                }

                alert(data.message);
            } catch (error) {
                console.error(error);
                alert(
                    'خطایی در افزودن محصول به سبد خرید رخ داد.'
                );
            }
        });
    });

    document.querySelectorAll(
        '[data-product-action="favorite"][data-favorite-url]'
    ).forEach(button => {
        button.addEventListener('click', async () => {
            if (!isAuthenticated) {
                window.location.href = loginUrl;
                return;
            }

            try {
                const response = await post(
                    button.dataset.favoriteUrl
                );

                if (response.redirected) {
                    window.location.href = loginUrl;
                    return;
                }

                const data = await response.json();

                if (!response.ok || !data.success) {
                    alert(
                        data.message ||
                        'عملیات ناموفق بود.'
                    );
                    return;
                }

                const icon = button.querySelector('i');

                button.classList.toggle(
                    'active',
                    data.is_favorite
                );

                icon?.classList.toggle(
                    'fa-solid',
                    data.is_favorite
                );

                icon?.classList.toggle(
                    'fa-regular',
                    !data.is_favorite
                );

                alert(data.message);
            } catch (error) {
                console.error(error);
                alert(
                    'خطایی در علاقه‌مندی رخ داد.'
                );
            }
        });
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

    document.getElementById('scrollTopBtn')?.addEventListener(
        'click',
        event => {
            event.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    );
});
