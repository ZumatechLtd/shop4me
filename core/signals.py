from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Account, Requester


@receiver(post_save, sender=User, dispatch_uid='user_profile_and_account_creation')
def user_profile_and_account_creation(sender, instance, created, **kwargs):
    if created:
        account = Account.objects.create(name=instance.username)
        Requester.objects.create(user=instance, account=account)
