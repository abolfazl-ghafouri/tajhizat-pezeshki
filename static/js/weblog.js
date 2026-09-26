document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    const navOverlay = document.getElementById('navOverlay');
    const header = document.getElementById('header');

    function closeMenu() {
        hamburger?.classList.remove('active');
        navMenu?.classList.remove('active');
        navOverlay?.classList.remove('active');
        document.body.style.overflow = '';
    }

    function openMenu() {
        hamburger?.classList.add('active');
        navMenu?.classList.add('active');
        navOverlay?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hamburger?.addEventListener('click', () => {
        if (navMenu?.classList.contains('active')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    navOverlay?.addEventListener('click', closeMenu);

    navMenu?.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            closeMenu();
        }
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

    window.addEventListener('scroll', () => {
        header?.classList.toggle(
            'scrolled',
            window.scrollY > 20
        );
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
});
