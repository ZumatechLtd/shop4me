import uuid
from random import randint, choice
from string import ascii_lowercase

from django.contrib.auth.models import User

from core.models import Account, Item, Requester, Shopper, RequestedItem, Comment


def random_int(n=10):
    return randint(0, n)


def random_string():
    return str(uuid.uuid4())


def set_if_not_present(dictionary, key, value):
    dictionary.setdefault(key, value)


def set_if_not_present_or_falsish(dictionary, key, value):
    if key not in dictionary or not dictionary[key]:
        dictionary[key] = value


def get_or_create(model, d):
    return model.objects.get_or_create(**d)[0]


def create_account(**kwargs):
    d = kwargs.copy()
    set_if_not_present(d, 'name', random_string())
    return get_or_create(Account, d)


def create_user(**kwargs):
    d = kwargs.copy()
    set_if_not_present(d, 'username', '%s@%s.com' % (random_string(), random_string()))
    set_if_not_present(d, 'password', random_string())
    user = get_or_create(User, d)
    return user


def create_item(**kwargs):
    d = kwargs.copy()
    set_if_not_present_or_falsish(d, 'name', random_string())
    return get_or_create(Item, d)


def setup_profile_fields(**kwargs):
    d = kwargs.copy()
    set_if_not_present(d, 'user', create_user()),
    set_if_not_present(d, 'account', create_account()),
    return d


def create_requester(shoppers=[], **kwargs):
    d = kwargs.copy()
    d = setup_profile_fields(**d)
    requester = get_or_create(Requester, d)
    if shoppers:
        requester.add_shopper(*shoppers)
    requester.save()
    return requester


def create_shopper(**kwargs):
    d = kwargs.copy()
    d = setup_profile_fields(**d)
    return get_or_create(Shopper, d)


def create_requested_item(comments=[], **kwargs):
    d = kwargs.copy()
    set_if_not_present_or_falsish(d, 'requester', create_requester())
    set_if_not_present_or_falsish(d, 'item', create_item())
    set_if_not_present(d, 'quantity', random_int())
    set_if_not_present(d, 'priority', RequestedItem.LOW)
    requested_item = get_or_create(RequestedItem, d)
    for comment in comments:
        create_comment(**comment, requested_item=requested_item)
    return requested_item


def create_comment(**kwargs):
    d = kwargs.copy()
    set_if_not_present(d, 'author', create_user())
    set_if_not_present(d, 'body', random_string())
    set_if_not_present(d, 'requested_item', create_requested_item())
    return get_or_create(Comment, d)

