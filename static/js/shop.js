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

    const grid = document.getElementById('productsGrid');
    const viewButtons = document.querySelectorAll('.view-btn[data-view]');

    viewButtons.forEach(button => {
        button.addEventListener('click', () => {
            viewButtons.forEach(item => {
                item.classList.remove('active');
            });

            button.classList.add('active');

            if (grid) {
                grid.classList.toggle(
                    'list-view',
                    button.dataset.view === 'list'
                );
            }
        });
    });

    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const mobileFilter = document.querySelector('.mobile-filter-btn');

    function closeSidebar() {
        sidebar?.classList.remove('active');
        overlay?.classList.remove('active');
    }

    mobileFilter?.addEventListener('click', () => {
        sidebar?.classList.add('active');
        overlay?.classList.add('active');
    });

    overlay?.addEventListener('click', closeSidebar);

    const brandSearch = document.getElementById('brandSearch');

    brandSearch?.addEventListener('input', function () {
        const term = this.value.toLowerCase().trim();

        document.querySelectorAll('.brand-item').forEach(item => {
            item.style.display = item.textContent
                .toLowerCase()
                .includes(term)
                ? 'flex'
                : 'none';
        });
    });

    function digits(value) {
        return String(value ?? '').replace(
            /[۰-۹٠-٩]/g,
            character => {
                const fa = '۰۱۲۳۴۵۶۷۸۹';
                const ar = '٠١٢٣٤٥٦٧٨٩';
                const faIndex = fa.indexOf(character);

                if (faIndex >= 0) {
                    return String(faIndex);
                }

                const arIndex = ar.indexOf(character);
                return arIndex >= 0
                    ? String(arIndex)
                    : character;
            }
        );
    }

    function applyFilters() {
        const current = new URLSearchParams(
            window.location.search
        );

        const params = new URLSearchParams();

        const query = current.get('q');
        if (query) {
            params.set('q', query);
        }

        const category = current.get('category');
        if (category) {
            params.set('category', category);
        }

        document.querySelectorAll(
            'input[name="brand"]:checked'
        ).forEach(input => {
            params.append('brand', input.value);
        });

        const stock = document.querySelector(
            'input[name="stock"]:checked'
        );

        if (stock) {
            params.set('stock', stock.value);
        }

        const minInput = document.getElementById(
            'minPriceInput'
        );

        const maxInput = document.getElementById(
            'maxPriceInput'
        );

        const min = digits(
            minInput?.value.trim()
        ).replace(/,/g, '');

        const max = digits(
            maxInput?.value.trim()
        ).replace(/,/g, '');

        if (min) {
            params.set('min_price', min);
        }

        if (max) {
            params.set('max_price', max);
        }

        const sort = document.querySelector(
            '.sort-select'
        )?.value;

        if (sort) {
            params.set('sort', sort);
        }

        window.location.search = params.toString();
    }

    document.querySelector(
        '.apply-filter-btn'
    )?.addEventListener('click', applyFilters);

    document.querySelector(
        '.sort-select'
    )?.addEventListener('change', applyFilters);

    document.querySelector(
        '.clear-filters-btn'
    )?.addEventListener('click', () => {
        window.location.href = window.location.pathname;
    });

    async function post(url, formData) {
        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
    }

    function csrf() {
        return document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
        )?.value || '';
    }

    document.querySelectorAll(
        '.product-action-form'
    ).forEach(form => {
        form.addEventListener('submit', async event => {
            event.preventDefault();

            if (!isAuthenticated) {
                window.location.href = loginUrl;
                return;
            }

            try {
                const response = await post(
                    form.action,
                    new FormData(form)
                );

                if (response.redirected) {
                    window.location.href = loginUrl;
                    return;
                }

                const data = await response.json();

                if (!response.ok || !data.success) {
                    alert(
                        data.message ||
                        'افزودن به سبد خرید انجام نشد.'
                    );
                    return;
                }

                alert(data.message);
            } catch (error) {
                console.error(error);
                alert(
                    'خطایی در افزودن به سبد خرید رخ داد.'
                );
            }
        });
    });

    document.querySelectorAll(
        '.fav-btn[data-favorite-url]'
    ).forEach(button => {
        button.addEventListener('click', async () => {
            if (!isAuthenticated) {
                window.location.href = loginUrl;
                return;
            }

            const form = new FormData();
            form.set(
                'csrfmiddlewaretoken',
                csrf()
            );

            try {
                const response = await post(
                    button.dataset.favoriteUrl,
                    form
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

                button.classList.toggle(
                    'active',
                    data.is_favorite
                );

                const icon = button.querySelector('i');

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
        '[data-product-action="quick-view"]'
    ).forEach(button => {
        button.addEventListener('click', () => {
            const url = button.dataset.productDetailUrl;

            if (url) {
                window.location.href = url;
            }
        });
    });

    document.getElementById(
        'scrollTopBtn'
    )?.addEventListener('click', event => {
        event.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});
