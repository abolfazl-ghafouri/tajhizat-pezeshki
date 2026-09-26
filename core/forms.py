from django import forms

from .models import NewsletterSubscriber


class NewsletterForm(forms.ModelForm):

    class Meta:
        model = NewsletterSubscriber

        fields = (
            'email',
        )

        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'ایمیل خود را وارد کنید',
                    'class': 'newsletter-input',
                }
            ),
        }

        labels = {
            'email': 'ایمیل',
        }

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()