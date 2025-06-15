import jdatetime
from django import template

register = template.Library()

@register.filter
def to_jalali(value):
    if not value:
        return ''
    try:
        # اگر value هم datetime باشه هم date پشتیبانی می‌کنه
        if hasattr(value, 'date'):
            value = value.date()  # اگر datetime بود به date تبدیل کن

        jd = jdatetime.date.fromgregorian(date=value)
        return jd.strftime('%Y/%m/%d')
    except Exception:
        return value
