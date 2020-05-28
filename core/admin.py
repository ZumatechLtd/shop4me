from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import Account, Requester, RequestedItem, Shopper
from core.models import Item
from core.utils import date_string_from_datetime_object, localized_datetime_from_epoch_timestamp


def list_display_model_field(model, fieldname=None, order_field=None):
    model_name = model._meta.model_name.lower()
    def _(obj):
        try:
            if fieldname:
                related_obj = getattr(obj, fieldname)
                pk = related_obj.pk
            else:
                related_obj = obj
                pk = obj.pk
            if related_obj and pk:
                url = reverse('admin:%s_%s_change' % (model._meta.app_label, model_name), args=[pk])
                if url:
                    return mark_safe("<a href='%s'>%s</a>" % (url, related_obj))
                return related_obj
            return obj
        except AttributeError as e:
            return None
    _.short_description = model_name
    if fieldname or order_field:
        _.admin_order_field = order_field if order_field else fieldname
    return _


def epoch_timestamp_to_human_readable(field, alternative_name=None):
    def epoch_timestamp_as_human_readable(obj):
        value = getattr(obj, field)
        if value:
            return date_string_from_datetime_object(localized_datetime_from_epoch_timestamp(value), date_format='%Y-%m-%d %H:%M:%S %Z')
        return '-'
    if alternative_name:
        epoch_timestamp_as_human_readable.short_description = alternative_name.title()
    else:
        epoch_timestamp_as_human_readable.short_description = field.title()
    epoch_timestamp_as_human_readable.admin_order_field = field
    return epoch_timestamp_as_human_readable


class RequesterModelAdmin(admin.ModelAdmin):
    fields = ['user', 'account', 'shoppers']
    list_display = ['user', 'account', 'get_invite_link']

    def get_invite_link(self, obj):
        return mark_safe('<a href=%s> Invite shopper </a>' % obj.invite_link)


class RequestedItemModelAdmin(admin.ModelAdmin):
    list_display = ['id', list_display_model_field(Requester, 'requester'), list_display_model_field(Item, 'item'),
                    'quantity', 'priority', list_display_model_field(Shopper, 'shopper'),
                    epoch_timestamp_to_human_readable('claimed_epoch_timestamp')]
    list_filter = ['priority']


admin.site.register(Account)
admin.site.register(Requester, RequesterModelAdmin)
admin.site.register(Shopper)
admin.site.register(Item)
admin.site.register(RequestedItem, RequestedItemModelAdmin)

