import uuid
from django.utils import timezone
from urllib.parse import urljoin

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.urls import reverse


class Account(models.Model):
    name = models.CharField(max_length=200)


class Profile(models.Model):
    REQUESTER = 'requester'
    SHOPPER = 'shopper'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='%(class)s_profiles')

    @classmethod
    def get_profile_model(cls, account_type):
        return {
            cls.REQUESTER: Requester,
            cls.SHOPPER: Shopper,
        }[account_type]

    class Meta:
        abstract = True


class Shopper(Profile):

    def claim_requested_item(self, requested_item):
        requested_item.shopper = self
        requested_item.claimed_epoch_timestamp = timezone.now().timestamp()
        requested_item.save()

    def __str__(self):
        return 'Shopper - %s' % self.user.username


class Requester(Profile):
    shoppers = models.ManyToManyField(Shopper, blank=True, null=True, related_name='requesters')
    invite_token = models.CharField(default=uuid.uuid4, max_length=200)

    def add_shopper(self, shopper):
        self.shoppers.add(shopper)
        self.invite_token = uuid.uuid4()
        self.save()

    def remove_shopper(self, shopper):
        self.shoppers.remove(shopper)
        self.save()

    @property
    def invite_link(self):
        return urljoin(settings.SITE_URL, reverse('core:add-shopper', kwargs={'pk': self.pk, 'invite_token': self.invite_token}))

    def __str__(self):
        return 'Requester - %s' % self.user.username


class Item(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return '%s' % self.name


class RequestedItemQueryset(models.QuerySet):
    def for_user(self, user):
        return self.filter(requester__user=user)


class RequestedItem(models.Model):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    priority_levels = (
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High')
    )
    objects = models.Manager.from_queryset(RequestedItemQueryset)()
    requester = models.ForeignKey(Requester, on_delete=models.CASCADE, related_name='requested_items')
    shopper = models.ForeignKey(Shopper, on_delete=models.CASCADE, blank=True, null=True, related_name='assigned_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    priority = models.IntegerField(choices=priority_levels, max_length=100)
    claimed_epoch_timestamp = models.BigIntegerField(blank=True, null=True)

    @property
    def is_claimed(self):
        return self.shopper is not None
    
    @property
    def priority_string(self):
        return dict((key, value) for key, value in self.priority_levels)[self.priority]
    
    class Meta:
        ordering = ['-priority']


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_item = models.ForeignKey(RequestedItem, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
