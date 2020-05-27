from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='%(class)s_profiles')

    class Meta:
        abstract = True


class Shopper(Profile):
    pass


class Requester(Profile):
    shoppers = models.ForeignKey(Shopper, models.CASCADE, blank=True, null=True)


class Item(models.Model):
    name = models.CharField(max_length=300)


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

    class Meta:
        ordering = ['-priority']
