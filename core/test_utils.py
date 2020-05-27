from random import randint, choice
from string import ascii_lowercase

from django.contrib.auth.models import User

from core import models as core_models


def random_int(n=10):
    return randint(0, n)


def random_string(n=10):
    return "".join(choice(ascii_lowercase) for _ in range(n))


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
    return get_or_create(core_models.Account, d)


def create_user(**kwargs):
    d = kwargs.copy()
    set_if_not_present(d, 'username', '%s@%s.com' % (random_string(), random_string()))
    set_if_not_present(d, 'password', random_string())
    return get_or_create(User, d)


def create_item(**kwargs):
    d = kwargs.copy()
    set_if_not_present_or_falsish(d, 'name', random_string())
    return get_or_create(core_models.Item, d)


def create_requester(**kwargs):
    d = kwargs.copy()
    set_if_not_present(d, 'user', create_user()),
    set_if_not_present(d, 'account', create_account())
    return get_or_create(core_models.Requester, d)


def create_requested_item(**kwargs):
    d = kwargs.copy()
    set_if_not_present_or_falsish(d, 'requester', create_requester())
    set_if_not_present_or_falsish(d, 'item', create_item())
    set_if_not_present(d, 'quantity', random_int())
    set_if_not_present(d, 'priority', core_models.RequestedItem.LOW)
    return get_or_create(core_models.RequestedItem, d)

