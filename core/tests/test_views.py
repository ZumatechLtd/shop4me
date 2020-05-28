from django.test import TestCase
from django.urls import reverse

from core.tests import utils as test_utils


class ViewTestCase(TestCase):
    def get(self, path, **kwargs):
        return self.client.get(path, **kwargs)

    def post(self, path, **kwargs):
        return self.client.post(path, **kwargs)

    def assertResponseOK(self, response, msg=None):
        self.assertResponseStatusCode(response, 200, msg)

    def assertResponseIsRedirect(self, response, msg=None):
        self.assertResponseStatusCode(response, 302, msg)

    def assertResponseIsMethodNotAllowed(self, response, msg=None):
        self.assertResponseStatusCode(response, 405, msg)

    def assertResponseNotFound(self, response):
        self.assertEqual(response.status_code, 404)

    def assertResponseStatusCode(self, response, expected_status_code, msg=None):
        self.assertEqual(response.status_code, expected_status_code, msg)

    def assertObjectExists(self, model, *args, **kwargs):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            self.fail('%s should exist (%s, %s)' % (model, args, kwargs))

    def login_user(self, user):
        self.client.force_login(user)


class AddShopperViewTests(ViewTestCase):
    def test_user_must_be_logged_in_to_accept_invite(self):
        requester = test_utils.create_requester()
        shopper = test_utils.create_shopper()
        resp = self.get(requester.invite_link)
        self.assertResponseIsRedirect(resp)
        self.assertNotIn(shopper, requester.shoppers.all())

    def test_shopper_can_accept_invite(self):
        requester = test_utils.create_requester()
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        self.get(requester.invite_link)
        self.assertIn(shopper, requester.shoppers.all())

    def test_requester_cannot_accept_invite(self):
        requester_one = test_utils.create_requester()
        requester_two = test_utils.create_requester()
        self.login_user(requester_two.user)
        response = self.get(requester_one.invite_link)
        self.assertResponseNotFound(response)

    def test_invite_link_is_updated_once_invite_is_accepted(self):
        requester = test_utils.create_requester()
        original_invite_token = requester.invite_token
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        self.get(requester.invite_link)
        self.assertIn(shopper, requester.shoppers.all())
        requester.refresh_from_db()
        self.assertNotEqual(original_invite_token, requester.invite_token)


class RemoveShopperViewTests(ViewTestCase):
    def remove_shopper(self, requester, shopper):
        return self.client.get(reverse('core:remove-shopper', args=[shopper.pk]))

    def test_requester_can_remove_shopper(self):
        shopper = test_utils.create_shopper()
        requester = test_utils.create_requester(shoppers=[shopper])
        self.assertIn(shopper, requester.shoppers.all())
        self.login_user(requester.user)
        self.remove_shopper(requester, shopper)
        self.assertNotIn(shopper, requester.shoppers.all())

    def test_shopper_cannot_remove_shopper(self):
        shopper = test_utils.create_shopper()
        requester = test_utils.create_requester(shoppers=[shopper])
        self.assertIn(shopper, requester.shoppers.all())
        self.login_user(shopper.user)
        resp = self.remove_shopper(shopper, shopper)
        self.assertResponseNotFound(resp)
