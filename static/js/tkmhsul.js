(function () {
    const body = document.body;
    const loginUrl = body.dataset.loginUrl || '/accounts/login/';

    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');

    function openMenu() {
        hamburger?.classList.add('active');
        navMenu?.classList.add('active');
        body.classList.add('menu-open');
    }

    function closeMenu() {
        hamburger?.classList.remove('active');
        navMenu?.classList.remove('active');
        body.classList.remove('menu-open');
    }

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', event => {
            event.stopPropagation();

            if (navMenu.classList.contains('active')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });

        document.addEventListener('keydown', event => {
            if (
                event.key === 'Escape' &&
                navMenu.classList.contains('active')
            ) {
                closeMenu();
            }
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

    const mainImage = document.getElementById('main-image');
    const thumbs = document.querySelectorAll('.thumb');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const slider = document.getElementById('slider');

    if (mainImage && thumbs.length && slider) {
        const images = Array.from(thumbs)
            .map(thumb => thumb.querySelector('img')?.src)
            .filter(Boolean);

        let current = 0;

        function changeImage(index) {
            if (!images[index] || index === current) return;

            current = index;
            mainImage.style.opacity = '0';

            setTimeout(() => {
                mainImage.src = images[current];
                mainImage.style.opacity = '1';
            }, 150);

            thumbs.forEach(thumb => {
                thumb.classList.remove('active');
            });

            thumbs[current]?.classList.add('active');
            thumbs[current]?.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }

        thumbs.forEach((thumb, index) => {
            thumb.addEventListener('click', event => {
                event.preventDefault();
                changeImage(index);
            });
        });

        nextBtn?.addEventListener('click', event => {
            event.preventDefault();
            changeImage(
                (current + 1) % images.length
            );
        });

        prevBtn?.addEventListener('click', event => {
            event.preventDefault();
            changeImage(
                (current - 1 + images.length) % images.length
            );
        });

        let touchStartX = 0;

        slider.addEventListener(
            'touchstart',
            event => {
                touchStartX = event.changedTouches[0].screenX;
            },
            { passive: true }
        );

        slider.addEventListener(
            'touchend',
            event => {
                const diff = touchStartX -
                    event.changedTouches[0].screenX;

                if (Math.abs(diff) > 40) {
                    if (diff > 0) {
                        changeImage(
                            (current + 1) % images.length
                        );
                    } else {
                        changeImage(
                            (current - 1 + images.length) % images.length
                        );
                    }
                }
            }
        );

        document.addEventListener('keydown', event => {
            if (event.key === 'ArrowLeft') {
                changeImage(
                    (current + 1) % images.length
                );
            }

            if (event.key === 'ArrowRight') {
                changeImage(
                    (current - 1 + images.length) % images.length
                );
            }
        });
    }

    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');
    const tabsContainer = document.getElementById('tabsContainer');

    tabs.forEach(tab => {
        tab.addEventListener('click', event => {
            event.preventDefault();

            const targetId = tab.dataset.tab;

            tabs.forEach(item => {
                item.classList.remove('active');
            });

            contents.forEach(item => {
                item.classList.remove('active');
            });

            tab.classList.add('active');
            document.getElementById(targetId)?.classList.add('active');

            tab.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        });
    });

    if (tabsContainer) {
        let isDown = false;
        let startX = 0;
        let scrollLeftPos = 0;

        tabsContainer.addEventListener('mousedown', event => {
            isDown = true;
            tabsContainer.style.cursor = 'grabbing';
            startX = event.pageX - tabsContainer.offsetLeft;
            scrollLeftPos = tabsContainer.scrollLeft;
        });

        tabsContainer.addEventListener('mouseleave', () => {
            isDown = false;
            tabsContainer.style.cursor = 'default';
        });

        tabsContainer.addEventListener('mouseup', () => {
            isDown = false;
            tabsContainer.style.cursor = 'default';
        });

        tabsContainer.addEventListener('mousemove', event => {
            if (!isDown) return;

            event.preventDefault();

            const x = event.pageX - tabsContainer.offsetLeft;
            const walk = (x - startX) * 1.5;
            tabsContainer.scrollLeft = scrollLeftPos - walk;
        });
    }

    document.querySelectorAll('.faq-item').forEach(item => {
        const title = item.querySelector('h4');

        title?.addEventListener('click', event => {
            event.preventDefault();

            const isOpen = item.classList.contains('open');

            document.querySelectorAll('.faq-item').forEach(faq => {
                faq.classList.remove('open');

                const paragraph = faq.querySelector('p');

                if (paragraph) {
                    paragraph.style.maxHeight = null;
                }
            });

            if (!isOpen) {
                item.classList.add('open');

                const paragraph = item.querySelector('p');

                if (paragraph) {
                    paragraph.style.maxHeight =
                        paragraph.scrollHeight + 40 + 'px';
                }
            }
        });
    });

    const scrollTopBtn = document.getElementById('scrollTopBtn');

    if (scrollTopBtn) {
        scrollTopBtn.style.opacity = '0';
        scrollTopBtn.style.pointerEvents = 'none';
        scrollTopBtn.style.transition =
            'opacity 0.3s, transform 0.3s, box-shadow 0.3s';

        window.addEventListener('scroll', () => {
            const visible = window.scrollY > 400;
            scrollTopBtn.style.opacity = visible ? '1' : '0';
            scrollTopBtn.style.pointerEvents = visible
                ? 'auto'
                : 'none';
        });

        scrollTopBtn.addEventListener('click', event => {
            event.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    window.addEventListener('resize', () => {
        if (
            window.innerWidth > 992 &&
            navMenu?.classList.contains('active')
        ) {
            closeMenu();
        }
    });

    const csrfToken = document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    )?.value || '';

    async function postAction(url, data = {}) {
        const formData = new FormData();
        formData.set(
            'csrfmiddlewaretoken',
            csrfToken
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

    const buyButton = document.getElementById('buyProductBtn');

    buyButton?.addEventListener('click', async () => {
        const url = buyButton.dataset.cartUrl;

        if (!url) return;

        try {
            const response = await postAction(url);

            if (response.redirected) {
                window.location.href = loginUrl;
                return;
            }

            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(
                    data.message ||
                    'افزودن محصول انجام نشد.'
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

    const favoriteButton = document.getElementById(
        'favoriteProductBtn'
    );

    favoriteButton?.addEventListener('click', async () => {
        const url = favoriteButton.dataset.favoriteUrl;

        if (!url) return;

        try {
            const response = await postAction(url);

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

            favoriteButton.classList.toggle(
                'active',
                data.is_favorite
            );

            favoriteButton.classList.toggle(
                'fa-solid',
                data.is_favorite
            );

            favoriteButton.classList.toggle(
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
})();
