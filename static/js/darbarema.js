document.addEventListener('DOMContentLoaded', function () {
    const stats = document.querySelectorAll('.stat-card .number');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.5 });

        stats.forEach(stat => {
            stat.style.opacity = '0.5';
            stat.style.transform = 'translateY(10px)';
            stat.style.transition = 'all 0.5s ease';
            observer.observe(stat);
        });
    }

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
