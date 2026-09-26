from django import forms
from django.core.exceptions import ValidationError

from accounts.models import User


def normalize_phone(phone):
    phone = phone.strip()

    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'

    translation_table = str.maketrans(
        persian_digits + arabic_digits,
        english_digits + english_digits
    )

    phone = phone.translate(translation_table)

    phone = ''.join(
        char for char in phone
        if char.isdigit()
    )

    if len(phone) == 10 and phone.startswith('9'):
        phone = '0' + phone

    if len(phone) != 11 or not phone.startswith('09'):
        raise ValidationError(
            'شماره موبایل وارد شده صحیح نیست.'
        )

    return phone


class LoginOTPForm(forms.Form):

    phone = forms.CharField(
        max_length=11
    )

    def clean_phone(self):
        return normalize_phone(
            self.cleaned_data['phone']
        )


class RegisterOTPForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        min_length=2
    )

    phone = forms.CharField(
        max_length=11
    )

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_phone(self):
        return normalize_phone(
            self.cleaned_data['phone']
        )


class VerifyOTPForm(forms.Form):

    phone = forms.CharField(
        max_length=11
    )

    code = forms.CharField(
        max_length=6,
        min_length=6
    )

    def clean_phone(self):
        return normalize_phone(
            self.cleaned_data['phone']
        )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()

        if not code.isdigit():
            raise ValidationError(
                'کد OTP باید عددی باشد.'
            )

        return code


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User

        fields = (
            'full_name',
            'email',
            'avatar',
        )

        labels = {
            'full_name': 'نام و نام خانوادگی',
            'email': 'ایمیل',
            'avatar': 'تصویر پروفایل',
        }