from django.contrib import admin
from django.utils.safestring import mark_safe

from core.models import Account, Requester, RequestedItem, Shopper
from core.models import Item


class RequesterModelAdmin(admin.ModelAdmin):
    fields = ['user', 'account', 'shoppers']
    list_display = ['user', 'account', 'get_invite_link']

    def get_invite_link(self, obj):
        return mark_safe('<a href=%s> Invite shopper </a>' % obj.invite_link)


class RequestedItemModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'requester', 'item', 'quantity', 'priority', 'shopper']
    list_filter = ['priority']


admin.site.register(Account)
admin.site.register(Requester, RequesterModelAdmin)
admin.site.register(Shopper)
admin.site.register(Item)
admin.site.register(RequestedItem, RequestedItemModelAdmin)

