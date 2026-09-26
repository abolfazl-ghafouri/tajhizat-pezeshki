from django import template


register = template.Library()


@register.filter
def fa_num(value):
    if value is None:
        return ''

    translation = str.maketrans(
        '0123456789',
        '۰۱۲۳۴۵۶۷۸۹'
    )

    return str(value).translate(translation)


@register.filter
def fa_price(value):
    if value is None:
        return ''

    formatted = f'{value:,}'.replace(',', '٬')

    return (
        str(formatted)
        .translate(
            str.maketrans(
                '0123456789',
                '۰۱۲۳۴۵۶۷۸۹'
            )
        )
        + ' تومان'
    )