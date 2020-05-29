from django import template

from core.utils import localized_datetime_from_epoch_timestamp, date_string_from_datetime_object

register = template.Library()


@register.filter
def datetime_from_timestamp(value):
    if value is not None:
        return date_string_from_datetime_object(localized_datetime_from_epoch_timestamp(value), date_format='%Y-%m-%d %H:%M:%S %Z')
    return None
