from django import forms

from .models import (
    ConsultationRequest,
    ContactMessage,
    Ticket,
)


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = (
            'subject',
            'category',
            'priority',
            'related_product',
            'message',
        )

        widgets = {
            'message': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': 'مشکل یا درخواست خود را توضیح دهید...',
                }
            ),
        }

    def clean_subject(self):
        subject = self.cleaned_data['subject'].strip()

        if len(subject) < 3:
            raise forms.ValidationError(
                'موضوع تیکت خیلی کوتاه است.'
            )

        return subject

    def clean_message(self):
        message = self.cleaned_data['message'].strip()

        if len(message) < 10:
            raise forms.ValidationError(
                'متن تیکت باید حداقل ۱۰ کاراکتر باشد.'
            )

        return message


class ContactMessageForm(forms.ModelForm):

    class Meta:
        model = ContactMessage

        fields = (
            'name',
            'email',
            'phone',
            'subject',
            'message',
        )

        widgets = {
            'message': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': 'متن پیام خود را بنویسید...',
                }
            ),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_subject(self):
        return self.cleaned_data['subject'].strip()

    def clean_message(self):
        message = self.cleaned_data['message'].strip()

        if len(message) < 5:
            raise forms.ValidationError(
                'متن پیام خیلی کوتاه است.'
            )

        return message

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if not phone:
            return phone

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


class ConsultationRequestForm(
    forms.ModelForm
):

    class Meta:
        model = ConsultationRequest

        fields = (
            'name',
            'phone',
            'email',
            'message',
        )

        widgets = {
            'message': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'توضیحات درخواست خود را وارد کنید...',
                }
            ),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()

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