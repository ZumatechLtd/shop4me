from django.db import IntegrityError
from django.test import TestCase

from core.models import RequestedItem
from core import test_utils


# Create your tests here.
class ModelTests(TestCase):
    def test_requested_items_default_ordering_priority_descending(self):
        medium = test_utils.create_requested_item(priority=RequestedItem.MEDIUM)
        high = test_utils.create_requested_item(priority=RequestedItem.HIGH)
        low = test_utils.create_requested_item(priority=RequestedItem.LOW)
        self.assertEqual(list(RequestedItem.objects.all()), [high, medium, low])
