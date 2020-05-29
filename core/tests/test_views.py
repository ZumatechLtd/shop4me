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


class RequestedItemsClaimViewTest(ViewTestCase):
    def setUp(self):
        super(RequestedItemsClaimViewTest, self).setUp()
        self.shopper = test_utils.create_shopper()

    def claim_item(self, requested_item):
        return self.get(reverse('core:requested-item-claim', args=[requested_item.pk]))

    def test_shopper_can_claim_requested_item(self):
        requested_item = test_utils.create_requested_item()
        self.login_user(self.shopper.user)
        self.claim_item(requested_item)
        requested_item.refresh_from_db()
        self.assertEqual(requested_item.shopper, self.shopper)


class CommentViewTests(ViewTestCase):
    def create_comment(self, requested_item, data):
        return self.post(reverse('core:comment-create', args=[requested_item.pk]), data=data)

    def delete_comment(self, comment):
        return self.post(reverse('core:comment-delete', args=[comment.pk]))

    def test_user_can_create_comment(self):
        comment_body = 'Bar'
        requested_item = test_utils.create_requested_item()
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        self.create_comment(requested_item, {'body': comment_body})
        requested_item.refresh_from_db()
        self.assertEqual(requested_item.comments.count(), 1)
        comment = requested_item.comments.first()
        self.assertEqual(comment_body, comment.body)

    def test_user_can_delete_comment(self):
        shopper = test_utils.create_shopper()
        requested_item = test_utils.create_requested_item(shopper=shopper)
        comment = test_utils.create_comment(requested_item=requested_item)
        self.assertEqual(requested_item.comments.count(), 1)
        self.login_user(shopper.user)
        self.delete_comment(comment)
        self.assertEqual(requested_item.comments.count(), 0)
