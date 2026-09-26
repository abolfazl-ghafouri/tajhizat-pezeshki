from django import forms

from accounts.models import Address


class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        required=True,
    )

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()


class CheckoutForm(forms.Form):

    customer_name = forms.CharField(
        max_length=150,
        required=True,
    )

    phone = forms.CharField(
        max_length=11,
        required=True,
    )

    city = forms.CharField(
        max_length=100,
        required=True,
    )

    address = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
            }
        ),
    )

    postal_code = forms.CharField(
        max_length=10,
        required=False,
    )

    def clean_customer_name(self):
        return self.cleaned_data['customer_name'].strip()

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        # تبدیل اعداد فارسی و عربی به انگلیسی
        translation_table = str.maketrans(
            '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩',
            '01234567890123456789',
        )

        phone = phone.translate(
            translation_table
        )

        phone = ''.join(
            char for char in phone
            if char.isdigit()
        )

        if len(phone) == 10 and phone.startswith('9'):
            phone = '0' + phone

        if len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError(
                'شماره موبایل صحیح نیست.'
            )

        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code'].strip()

        if postal_code:
            translation_table = str.maketrans(
                '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩',
                '01234567890123456789',
            )

            postal_code = postal_code.translate(
                translation_table
            )

            postal_code = ''.join(
                char for char in postal_code
                if char.isdigit()
            )

            if len(postal_code) != 10:
                raise forms.ValidationError(
                    'کد پستی باید ۱۰ رقم باشد.'
                )

        return postal_code


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address

        fields = (
            'title',
            'recipient_name',
            'phone',
            'province',
            'city',
            'address',
            'postal_code',
            'is_default',
        )

        widgets = {
            'address': forms.Textarea(
                attrs={
                    'rows': 4,
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        translation_table = str.maketrans(
            '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩',
            '01234567890123456789',
        )

        phone = phone.translate(
            translation_table
        )

        phone = ''.join(
            char for char in phone
            if char.isdigit()
        )

        if len(phone) == 10 and phone.startswith('9'):
            phone = '0' + phone

        if len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError(
                'شماره موبایل صحیح نیست.'
            )

        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code'].strip()

        if postal_code:
            translation_table = str.maketrans(
                '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩',
                '01234567890123456789',
            )

            postal_code = postal_code.translate(
                translation_table
            )

            postal_code = ''.join(
                char for char in postal_code
                if char.isdigit()
            )

            if len(postal_code) != 10:
                raise forms.ValidationError(
                    'کد پستی باید ۱۰ رقم باشد.'
                )

        return postal_code