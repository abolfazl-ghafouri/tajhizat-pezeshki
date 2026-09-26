(function () {
    const tabLogin = document.getElementById('tabLogin');
    const tabRegister = document.getElementById('tabRegister');
    const formLogin = document.getElementById('formLogin');
    const formRegister = document.getElementById('formRegister');
    const otpSection = document.getElementById('otpSection');
    const otpBoxes = document.getElementById('otpBoxes');
    const otpInputs = otpBoxes?.querySelectorAll('.otp-input') || [];
    const btnLoginSubmit = document.getElementById('btnLoginSubmit');
    const btnRegisterSubmit = document.getElementById('btnRegisterSubmit');
    const btnOtpVerify = document.getElementById('btnOtpVerify');
    const btnBack = document.getElementById('btnBack');
    const countdownTimer = document.getElementById('countdownTimer');
    const resendLink = document.getElementById('resendLink');
    const otpPhoneDisplay = document.getElementById('otpPhoneDisplay');
    const successCheck = document.getElementById('successCheck');
    const phoneLogin = document.getElementById('phoneLogin');
    const phoneRegister = document.getElementById('phoneRegister');
    const fullName = document.getElementById('fullName');

    if (!formLogin || !formRegister || !otpSection) {
        return;
    }

    let currentMode = 'login';
    let currentPhone = '';
    let countdownInterval = null;
    let countdownSeconds = 120;

    function getCSRFToken() {
        return document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
        )?.value || '';
    }

    function normalizeDigits(value) {
        const map = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        };

        return [...String(value || '')]
            .map(character => map[character] ?? character)
            .join('');
    }

    function normalizePhone(phone) {
        return normalizeDigits(phone)
            .replace(/[^0-9]/g, '');
    }

    function validPhone(phone) {
        const normalized = normalizePhone(phone);

        if (
            normalized.length === 10 &&
            normalized.startsWith('9')
        ) {
            return '0' + normalized;
        }

        if (
            normalized.length === 11 &&
            normalized.startsWith('0')
        ) {
            return normalized;
        }

        return '';
    }

    function formatPhone(phone) {
        const digits = [
            '۰', '۱', '۲', '۳', '۴',
            '۵', '۶', '۷', '۸', '۹'
        ];

        const value = [...phone]
            .map(character => digits[Number(character)] ?? character)
            .join('');

        return value.length === 11
            ? `${value.slice(0, 4)} ${value.slice(4, 7)} ${value.slice(7)}`
            : value;
    }

    function shake(element) {
        if (!element) return;

        element.style.animation = 'none';
        void element.offsetWidth;
        element.style.animation = 'shake 0.5s ease';

        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }

    function resetOTP() {
        otpInputs.forEach(input => {
            input.value = '';
            input.classList.remove('filled', 'error');
        });

        otpInputs[0]?.focus();
    }

    function getOTP() {
        return [...otpInputs]
            .map(input => normalizeDigits(input.value))
            .join('');
    }

    function setCountdown() {
        const minutes = Math.floor(
            countdownSeconds / 60
        );

        const seconds = String(
            countdownSeconds % 60
        ).padStart(2, '0');

        const text = `${minutes}:${seconds}`.replace(
            /[0-9]/g,
            digit => '۰۱۲۳۴۵۶۷۸۹'[Number(digit)]
        );

        if (countdownTimer) {
            countdownTimer.textContent = text;
            countdownTimer.classList.toggle(
                'urgent',
                countdownSeconds <= 20
            );
        }
    }

    function stopCountdown() {
        if (countdownInterval) {
            clearInterval(countdownInterval);
        }

        countdownInterval = null;
    }

    function startCountdown() {
        stopCountdown();

        countdownSeconds = 120;
        setCountdown();

        resendLink?.classList.add('disabled');

        countdownInterval = setInterval(() => {
            countdownSeconds -= 1;
            setCountdown();

            if (countdownSeconds <= 0) {
                stopCountdown();
                resendLink?.classList.remove('disabled');

                if (resendLink) {
                    resendLink.textContent = 'ارسال مجدد کد';
                }
            }
        }, 1000);
    }

    function switchTab(mode) {
        currentMode = mode;

        tabLogin?.classList.toggle(
            'active',
            mode === 'login'
        );

        tabRegister?.classList.toggle(
            'active',
            mode === 'register'
        );

        formLogin.style.display =
            mode === 'login' ? 'flex' : 'none';

        formRegister.style.display =
            mode === 'register' ? 'flex' : 'none';

        otpSection.style.display = 'none';
        otpSection.classList.remove('visible');

        resetOTP();
        stopCountdown();

        countdownSeconds = 120;
        setCountdown();

        resendLink?.classList.add('disabled');

        if (resendLink) {
            resendLink.textContent = 'ارسال مجدد';
        }

        successCheck?.classList.remove('visible');
    }

    function showOTP(phone) {
        currentPhone = phone;

        formLogin.style.display = 'none';
        formRegister.style.display = 'none';

        otpSection.style.display = 'flex';
        void otpSection.offsetWidth;
        otpSection.classList.add('visible');

        if (otpPhoneDisplay) {
            otpPhoneDisplay.textContent = formatPhone(phone);
        }

        successCheck?.classList.remove('visible');

        if (btnOtpVerify) {
            btnOtpVerify.disabled = false;
            btnOtpVerify.textContent = 'تایید کد';
        }

        resetOTP();
        startCountdown();
    }

    async function requestOTP(form, phoneInput) {
        const phone = validPhone(
            phoneInput?.value.trim()
        );

        if (!phone) {
            shake(phoneInput);
            return;
        }

        if (
            currentMode === 'register' &&
            (fullName?.value.trim().length || 0) < 2
        ) {
            shake(fullName);
            return;
        }

        const formData = new FormData(form);
        formData.set('phone', phone);

        if (currentMode === 'register') {
            formData.set(
                'full_name',
                fullName?.value.trim() || ''
            );
        }

        const button = currentMode === 'login'
            ? btnLoginSubmit
            : btnRegisterSubmit;

        if (!button) return;

        const oldText = button.textContent;
        button.disabled = true;
        button.textContent = 'در حال ارسال...';

        try {
            const response = await fetch(
                form.dataset.backendEndpoint,
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
                alert(
                    data.message ||
                    'درخواست ناموفق بود.'
                );
                return;
            }

            showOTP(data.phone || phone);
        } catch (error) {
            console.error(error);
            alert(
                'خطایی در ارتباط با سرور رخ داد.'
            );
        } finally {
            button.disabled = false;
            button.textContent = oldText;
        }
    }

    tabLogin?.addEventListener(
        'click',
        () => switchTab('login')
    );

    tabRegister?.addEventListener(
        'click',
        () => switchTab('register')
    );

    otpInputs.forEach((input, index) => {
        input.addEventListener('input', event => {
            event.target.value = normalizeDigits(
                event.target.value
            ).replace(/[^0-9]/g, '').slice(0, 1);

            if (event.target.value) {
                event.target.classList.add('filled');
                event.target.classList.remove('error');

                if (index < otpInputs.length - 1) {
                    otpInputs[index + 1].focus();
                }
            }
        });

        input.addEventListener('keydown', event => {
            if (
                event.key === 'Backspace' &&
                !input.value &&
                index > 0
            ) {
                otpInputs[index - 1].focus();
            }
        });

        input.addEventListener('paste', event => {
            event.preventDefault();

            const value = normalizeDigits(
                event.clipboardData.getData('text')
            )
                .replace(/[^0-9]/g, '')
                .slice(0, 6);

            [...otpInputs].forEach((target, i) => {
                target.value = value[i] || '';
                target.classList.toggle(
                    'filled',
                    Boolean(value[i])
                );
                target.classList.remove('error');
            });

            otpInputs[
                Math.min(value.length, 5)
            ]?.focus();
        });
    });

    btnLoginSubmit?.addEventListener(
        'click',
        () => requestOTP(formLogin, phoneLogin)
    );

    btnRegisterSubmit?.addEventListener(
        'click',
        () => requestOTP(formRegister, phoneRegister)
    );

    btnOtpVerify?.addEventListener(
        'click',
        async () => {
            const code = getOTP();

            if (code.length !== 6) {
                otpInputs.forEach(input => {
                    if (!input.value) {
                        input.classList.add('error');
                    }
                });

                shake(btnOtpVerify);
                return;
            }

            btnOtpVerify.disabled = true;
            btnOtpVerify.textContent = 'در حال تایید...';

            const formData = new FormData();
            formData.set('phone', currentPhone);
            formData.set('code', code);
            formData.set('purpose', currentMode);
            formData.set(
                'csrfmiddlewaretoken',
                getCSRFToken()
            );

            try {
                const response = await fetch(
                    document.body.dataset.verifyUrl ||
                    '/accounts/verify-otp/',
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
                    alert(
                        data.message ||
                        'کد تایید اشتباه است.'
                    );

                    btnOtpVerify.disabled = false;
                    btnOtpVerify.textContent = 'تایید کد';
                    return;
                }

                successCheck?.classList.add('visible');
                btnOtpVerify.textContent = 'تایید شد ✓';

                stopCountdown();
                resendLink?.classList.add('disabled');

                if (countdownTimer) {
                    countdownTimer.textContent = '✓';
                }

                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 700);
            } catch (error) {
                console.error(error);
                alert('خطایی در تایید کد رخ داد.');

                btnOtpVerify.disabled = false;
                btnOtpVerify.textContent = 'تایید کد';
            }
        }
    );

    resendLink?.addEventListener(
        'click',
        async () => {
            if (
                resendLink.classList.contains('disabled')
            ) {
                return;
            }

            const form = currentMode === 'login'
                ? formLogin
                : formRegister;

            const input = currentMode === 'login'
                ? phoneLogin
                : phoneRegister;

            await requestOTP(form, input);
        }
    );

    btnBack?.addEventListener(
        'click',
        () => switchTab(currentMode)
    );

    phoneLogin?.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            btnLoginSubmit?.click();
        }
    });

    phoneRegister?.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            btnRegisterSubmit?.click();
        }
    });

    fullName?.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            btnRegisterSubmit?.click();
        }
    });

    setCountdown();

    if (window.location.hash === '#register') {
        switchTab('register');
    } else {
        switchTab('login');
    }
})();
