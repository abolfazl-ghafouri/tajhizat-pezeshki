from django import forms

from .models import ArticleComment


class ArticleCommentForm(forms.ModelForm):

    class Meta:
        model = ArticleComment

        fields = (
            'body',
        )

        widgets = {
            'body': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'نظر خود را بنویسید...',
                    'class': 'comment-body',
                }
            ),
        }

        labels = {
            'body': 'متن نظر',
        }

    def clean_body(self):
        body = self.cleaned_data['body'].strip()

        if len(body) < 5:
            raise forms.ValidationError(
                'متن نظر باید حداقل ۵ کاراکتر باشد.'
            )

        return body