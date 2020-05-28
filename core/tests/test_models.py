from django.test import TestCase

from core.tests import utils
from core.models import RequestedItem, Requester


class ModelTestCase(TestCase):
    pass


class RequestedItemModelTestCase(ModelTestCase):
    def test_requested_items_default_ordering_priority_descending(self):
        medium = utils.create_requested_item(priority=RequestedItem.MEDIUM)
        high = utils.create_requested_item(priority=RequestedItem.HIGH)
        low = utils.create_requested_item(priority=RequestedItem.LOW)
        self.assertEqual(list(RequestedItem.objects.all()), [high, medium, low])
