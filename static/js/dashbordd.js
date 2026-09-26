document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');
    const navItems = document.querySelectorAll('.nav-item[data-section]');
    const sections = document.querySelectorAll('.content-section');

    function closeSidebar() {
        sidebar?.classList.remove('open');
        overlay?.classList.remove('active');
        document.body.style.overflow = '';
    }

    function openSidebar() {
        sidebar?.classList.add('open');
        overlay?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hamburgerBtn?.addEventListener('click', openSidebar);
    closeBtn?.addEventListener('click', closeSidebar);
    overlay?.addEventListener('click', closeSidebar);

    function showSection(name) {
        sections.forEach(section => {
            section.classList.remove('active');
        });

        navItems.forEach(item => {
            item.classList.remove('active');
        });

        document.getElementById(
            `${name}-section`
        )?.classList.add('active');

        document.querySelector(
            `.nav-item[data-section="${name}"]`
        )?.classList.add('active');

        if (window.innerWidth <= 1024) {
            closeSidebar();
        }
    }

    window.navigateTo = showSection;

    navItems.forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();
            showSection(item.dataset.section);
        });
    });

    document.querySelectorAll(
        '.stat-card[data-navigate]'
    ).forEach(card => {
        card.addEventListener('click', () => {
            showSection(card.dataset.navigate);
        });
    });

    document.querySelectorAll(
        '[data-dashboard-section]'
    ).forEach(item => {
        item.addEventListener('click', () => {
            showSection(item.dataset.dashboardSection);
        });
    });

    const orderRows = document.querySelectorAll(
        '#orders-table tbody tr[data-status]'
    );

    document.querySelectorAll(
        '#order-filters .filter-tab'
    ).forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll(
                '#order-filters .filter-tab'
            ).forEach(item => {
                item.classList.remove('active');
            });

            tab.classList.add('active');

            const filter = tab.dataset.filter;

            orderRows.forEach(row => {
                const status = row.dataset.status;
                const visible =
                    filter === 'all' ||
                    (
                        filter === 'active' &&
                        ['paid', 'shipping'].includes(status)
                    ) ||
                    status === filter;

                row.style.display = visible ? '' : 'none';
            });
        });
    });

    function formatMoney() {
        document.querySelectorAll('.js-money').forEach(element => {
            const value = Number(
                String(element.textContent)
                    .replace(/[^0-9]/g, '')
            );

            if (!Number.isNaN(value)) {
                element.textContent = value.toLocaleString('fa-IR');
            }
        });
    }

    formatMoney();

    const csrf = () => document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    )?.value || '';

    // ============ MODALS ==========
    let activeModal = null;

    function closeDashboardModal() {
        if (!activeModal) return;

        activeModal.classList.remove('active');
        document.body.classList.remove('dashboard-modal-open');

        setTimeout(() => {
            activeModal?.remove();
            activeModal = null;
        }, 200);
    }

    function openDashboardModal({
        title,
        icon,
        content,
        onSubmit,
    }) {
        closeDashboardModal();

        const backdrop = document.createElement('div');
        backdrop.className = 'dashboard-modal-backdrop';

        backdrop.innerHTML = `
            <div class="dashboard-modal" role="dialog" aria-modal="true" aria-label="${title}">
                <div class="dashboard-modal-header">
                    <h2 class="dashboard-modal-title">
                        <span class="material-icons">${icon}</span>
                        ${title}
                    </h2>
                    <button type="button" class="dashboard-modal-close" aria-label="بستن">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div class="dashboard-modal-body">
                    ${content}
                </div>
            </div>
        `;

        document.body.appendChild(backdrop);
        activeModal = backdrop;
        document.body.classList.add('dashboard-modal-open');

        backdrop.querySelector('.dashboard-modal-close')?.addEventListener(
            'click',
            closeDashboardModal
        );

        backdrop.addEventListener('click', event => {
            if (event.target === backdrop) {
                closeDashboardModal();
            }
        });

        document.addEventListener('keydown', function escHandler(event) {
            if (event.key === 'Escape' && activeModal === backdrop) {
                closeDashboardModal();
                document.removeEventListener('keydown', escHandler);
            }
        });

        requestAnimationFrame(() => {
            backdrop.classList.add('active');
        });

        const form = backdrop.querySelector('form');

        form?.addEventListener('submit', async event => {
            event.preventDefault();
            await onSubmit(form, backdrop);
        });

        form?.querySelector('input, select, textarea')?.focus();

        return backdrop;
    }

    function showModalError(backdrop, message) {
        const errorBox = backdrop.querySelector('.modal-error');

        if (!errorBox) return;

        errorBox.textContent = message;
        errorBox.classList.add('show');
    }

    // ============ ADDRESS DELETE ============
    document.querySelectorAll(
        '[data-address-action="delete"]'
    ).forEach(button => {
        button.addEventListener('click', async () => {
            if (!confirm(
                'آیا از حذف این آدرس مطمئن هستید؟'
            )) {
                return;
            }

            const url = button.dataset.actionUrl;
            if (!url) return;

            const form = new FormData();
            form.set('csrfmiddlewaretoken', csrf());

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: form
                });

                if (response.ok) {
                    window.location.reload();
                    return;
                }

                alert('خطایی در حذف آدرس رخ داد.');
            } catch (error) {
                console.error(error);
                alert('خطایی در حذف آدرس رخ داد.');
            }
        });
    });

    // ============ EDIT ADDRESS ============
    document.querySelectorAll(
        '[data-address-action="edit"]'
    ).forEach(button => {
        button.addEventListener('click', () => {
            const content = `
                <div class="modal-error"></div>

                <form>
                    <div class="form-group">
                        <label>عنوان آدرس</label>
                        <input
                            name="title"
                            type="text"
                            value=""
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>نام گیرنده</label>
                        <input
                            name="recipient_name"
                            type="text"
                            value=""
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>شماره موبایل</label>
                        <input
                            name="phone"
                            type="text"
                            value=""
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>استان</label>
                        <input
                            name="province"
                            type="text"
                            value=""
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>شهر</label>
                        <input
                            name="city"
                            type="text"
                            value=""
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label>آدرس کامل</label>
                        <textarea
                            name="address"
                            required
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label>کد پستی</label>
                        <input
                            name="postal_code"
                            type="text"
                            value=""
                        >
                    </div>

                    <div class="form-group">
                        <label>
                            <input
                                name="is_default"
                                type="checkbox"
                                ${button.dataset.isDefault === '1' ? 'checked' : ''}
                            >
                            آدرس پیش‌فرض
                        </label>
                    </div>

                    <div class="dashboard-modal-footer">
                        <button type="button" class="btn btn-outline js-modal-cancel">
                            انصراف
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <span class="material-icons">save</span>
                            ذخیره آدرس
                        </button>
                    </div>
                </form>
            `;

            const backdrop = openDashboardModal({
                title: 'ویرایش آدرس',
                icon: 'edit_location_alt',
                content,
                onSubmit: async (form, modal) => {
                    const submitButton = form.querySelector(
                        'button[type="submit"]'
                    );

                    submitButton.disabled = true;
                    submitButton.textContent = 'در حال ذخیره...';

                    const formData = new FormData(form);
                    formData.append(
                        'csrfmiddlewaretoken',
                        csrf()
                    );

                    try {
                        const response = await fetch(
                            button.dataset.actionUrl,
                            {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest'
                                }
                            }
                        );

                        if (!response.ok) {
                            showModalError(
                                modal,
                                'اطلاعات آدرس صحیح نیست.'
                            );
                            submitButton.disabled = false;
                            submitButton.textContent = 'ذخیره آدرس';
                            return;
                        }

                        closeDashboardModal();
                        window.location.reload();
                    } catch (error) {
                        console.error(error);
                        showModalError(
                            modal,
                            'خطایی در ویرایش آدرس رخ داد.'
                        );
                        submitButton.disabled = false;
                        submitButton.textContent = 'ذخیره آدرس';
                    }
                },
            });

            backdrop.querySelector('[name="title"]').value = button.dataset.title || '';
            backdrop.querySelector('[name="recipient_name"]').value = button.dataset.recipientName || '';
            backdrop.querySelector('[name="phone"]').value = button.dataset.phone || '';
            backdrop.querySelector('[name="province"]').value = button.dataset.province || '';
            backdrop.querySelector('[name="city"]').value = button.dataset.city || '';
            backdrop.querySelector('[name="address"]').value = button.dataset.address || '';
            backdrop.querySelector('[name="postal_code"]').value = button.dataset.postalCode || '';

            backdrop.querySelector('.js-modal-cancel')?.addEventListener(
                'click',
                closeDashboardModal
            );
        });
    });

    // ============ CREATE ADDRESS ============
    const createAddressButton = document.querySelector(
        '[data-create-address-url]'
    );

    createAddressButton?.addEventListener('click', () => {
        const content = `
            <div class="modal-error"></div>

            <form>
                <div class="form-group">
                    <label>عنوان آدرس</label>
                    <input
                        name="title"
                        type="text"
                        value="آدرس اصلی"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>نام گیرنده</label>
                    <input
                        name="recipient_name"
                        type="text"
                        placeholder="نام و نام خانوادگی گیرنده"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>شماره موبایل</label>
                    <input
                        name="phone"
                        type="text"
                        placeholder="09123456789"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>استان</label>
                    <input
                        name="province"
                        type="text"
                        placeholder="استان"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>شهر</label>
                    <input
                        name="city"
                        type="text"
                        placeholder="شهر"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>آدرس کامل</label>
                    <textarea
                        name="address"
                        placeholder="آدرس کامل ارسال"
                        required
                    ></textarea>
                </div>

                <div class="form-group">
                    <label>کد پستی</label>
                    <input
                        name="postal_code"
                        type="text"
                        placeholder="۱۰ رقم"
                    >
                </div>

                <div class="form-group">
                    <label>
                        <input
                            name="is_default"
                            type="checkbox"
                            checked
                        >
                        آدرس پیش‌فرض
                    </label>
                </div>

                <div class="dashboard-modal-footer">
                    <button type="button" class="btn btn-outline js-modal-cancel">
                        انصراف
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <span class="material-icons">add_location</span>
                        ثبت آدرس
                    </button>
                </div>
            </form>
        `;

        const backdrop = openDashboardModal({
            title: 'افزودن آدرس جدید',
            icon: 'location_on',
            content,
            onSubmit: async (form, modal) => {
                const submitButton = form.querySelector(
                    'button[type="submit"]'
                );

                submitButton.disabled = true;
                submitButton.textContent = 'در حال ثبت...';

                const formData = new FormData(form);
                formData.append(
                    'csrfmiddlewaretoken',
                    csrf()
                );

                try {
                    const response = await fetch(
                        createAddressButton.dataset.createAddressUrl,
                        {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        }
                    );

                    if (!response.ok) {
                        showModalError(
                            modal,
                            'اطلاعات آدرس صحیح نیست.'
                        );
                        submitButton.disabled = false;
                        submitButton.textContent = 'ثبت آدرس';
                        return;
                    }

                    closeDashboardModal();
                    window.location.reload();
                } catch (error) {
                    console.error(error);
                    showModalError(
                        modal,
                        'خطایی در ثبت آدرس رخ داد.'
                    );
                    submitButton.disabled = false;
                    submitButton.textContent = 'ثبت آدرس';
                }
            },
        });

        backdrop.querySelector('.js-modal-cancel')?.addEventListener(
            'click',
            closeDashboardModal
        );
    });

    // ============ AJAX FORMS ============
    document.querySelectorAll(
        '[data-ajax-form]'
    ).forEach(form => {
        form.addEventListener('submit', async event => {
            event.preventDefault();

            if (form.dataset.ajaxForm === 'contact') {
                const emailInput = form.querySelector('[name="email"]');

                if (emailInput && !emailInput.value.trim()) {
                    alert('ابتدا ایمیل خود را در بخش اطلاعات حساب ثبت کنید.');
                    return;
                }
            }

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
                    'خطایی در ارسال اطلاعات رخ داد.'
                );
            }
        });
    });

    document.querySelectorAll(
        '.fav-card[data-product-detail-url]'
    ).forEach(card => {
        card.addEventListener('click', () => {
            window.location.href = card.dataset.productDetailUrl;
        });
    });

    const newOrderButton = document.querySelector(
        '[data-dashboard-action="new-order"]'
    );

    newOrderButton?.addEventListener('click', () => {
        const shopUrl = newOrderButton.dataset.shopUrl;

        if (shopUrl) {
            window.location.href = shopUrl;
        }
    });

    // ============ CREATE TICKET ============
    const createTicketButtons = document.querySelectorAll(
        '[data-create-ticket-url]'
    );

    createTicketButtons.forEach(createTicketButton => {
        createTicketButton.addEventListener('click', () => {
            const content = `
            <div class="modal-error"></div>

            <form>
                <div class="form-group">
                    <label>موضوع تیکت</label>
                    <input
                        name="subject"
                        type="text"
                        placeholder="موضوع درخواست خود را بنویسید"
                        required
                    >
                </div>

                <div class="form-group">
                    <label>دسته‌بندی</label>
                    <select name="category">
                        <option value="">انتخاب دسته‌بندی</option>
                        <option value="فنی">فنی</option>
                        <option value="سفارش">سفارش</option>
                        <option value="محصول">محصول</option>
                        <option value="مالی">مالی</option>
                        <option value="سایر">سایر</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>اولویت</label>
                    <select name="priority">
                        <option value="low">کم</option>
                        <option value="normal" selected>عادی</option>
                        <option value="high">زیاد</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>متن درخواست</label>
                    <textarea
                        name="message"
                        placeholder="مشکل یا درخواست خود را کامل توضیح دهید..."
                        required
                    ></textarea>
                </div>

                <div class="dashboard-modal-footer">
                    <button type="button" class="btn btn-outline js-modal-cancel">
                        انصراف
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <span class="material-icons">send</span>
                        ثبت تیکت
                    </button>
                </div>
            </form>
        `;

        const backdrop = openDashboardModal({
            title: 'ثبت تیکت جدید',
            icon: 'confirmation_number',
            content,
            onSubmit: async (form, modal) => {
                const submitButton = form.querySelector(
                    'button[type="submit"]'
                );

                submitButton.disabled = true;
                submitButton.textContent = 'در حال ثبت...';

                const formData = new FormData(form);
                formData.append(
                    'csrfmiddlewaretoken',
                    csrf()
                );

                try {
                    const response = await fetch(
                        createTicketButton.dataset.createTicketUrl,
                        {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        }
                    );

                    const data = await response.json();

                    if (!response.ok || !data.success) {
                        showModalError(
                            modal,
                            data.message || 'اطلاعات تیکت صحیح نیست.'
                        );
                        submitButton.disabled = false;
                        submitButton.textContent = 'ثبت تیکت';
                        return;
                    }

                    alert(
                        `${data.message}\nشماره تیکت: ${data.ticket_number}`
                    );

                    closeDashboardModal();
                    window.location.reload();
                } catch (error) {
                    console.error(error);
                    showModalError(
                        modal,
                        'خطایی در ثبت تیکت رخ داد.'
                    );
                    submitButton.disabled = false;
                    submitButton.textContent = 'ثبت تیکت';
                }
            },
        });

            backdrop.querySelector('.js-modal-cancel')?.addEventListener(
                'click',
                closeDashboardModal
            );
        });
    });

    document.querySelectorAll('.faq-item').forEach(item => {
        const title = item.querySelector('.faq-q');

        title?.addEventListener('click', () => {
            item.classList.toggle('open');
        });
    });
});
