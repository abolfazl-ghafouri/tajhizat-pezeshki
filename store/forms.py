from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):

    class Meta:
        model = ProductReview

        fields = (
            'rating',
            'body',
        )

        widgets = {
            'rating': forms.Select(
                choices=[
                    (5, '۵ ستاره'),
                    (4, '۴ ستاره'),
                    (3, '۳ ستاره'),
                    (2, '۲ ستاره'),
                    (1, '۱ ستاره'),
                ],
                attrs={
                    'class': 'review-rating',
                },
            ),

            'body': forms.Textarea(
                attrs={
                    'class': 'review-body',
                    'placeholder': 'نظر خود را درباره این محصول بنویسید...',
                    'rows': 5,
                },
            ),
        }

        labels = {
            'rating': 'امتیاز',
            'body': 'نظر شما',
        }

    def clean_rating(self):
        rating = self.cleaned_data['rating']

        if rating < 1 or rating > 5:
            raise forms.ValidationError(
                'امتیاز باید بین ۱ تا ۵ باشد.'
            )

        return rating

    def clean_body(self):
        body = self.cleaned_data['body'].strip()

        if len(body) < 5:
            raise forms.ValidationError(
                'متن نظر باید حداقل ۵ کاراکتر باشد.'
            )

        return body