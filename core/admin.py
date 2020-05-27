from django.contrib import admin

from core.models import Account, Requester, RequestedItem
from core.models import Item

# Register your models here.
admin.site.register(Account)
admin.site.register(Requester)
admin.site.register(Item)
admin.site.register(RequestedItem)

