document.addEventListener('DOMContentLoaded', function () {
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

    const scrollTopBtn = document.getElementById(
        'scrollTopBtn'
    );

    if (scrollTopBtn) {
        scrollTopBtn.style.display = 'none';

        window.addEventListener('scroll', () => {
            scrollTopBtn.style.display =
                window.scrollY > 400
                    ? 'flex'
                    : 'none';
        });

        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
