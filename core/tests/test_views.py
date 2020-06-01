from django.test import TestCase
from django.urls import reverse

from core.models import RequestedItem
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

    def assertResponseIsPermissionDenied(self, response):
        self.assertEqual(response.status_code, 403)

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
        print(response.content)
        self.assertResponseIsPermissionDenied(response)

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
    def remove_shopper(self, shopper):
        return self.get(reverse('core:remove-shopper', args=[shopper.pk]))

    def test_requester_can_remove_shopper(self):
        shopper = test_utils.create_shopper()
        requester = test_utils.create_requester(shoppers=[shopper])
        self.assertIn(shopper, requester.shoppers.all())
        self.login_user(requester.user)
        self.remove_shopper(shopper)
        self.assertNotIn(shopper, requester.shoppers.all())

    def test_shopper_cannot_remove_shopper(self):
        shopper = test_utils.create_shopper()
        requester = test_utils.create_requester(shoppers=[shopper])
        self.assertIn(shopper, requester.shoppers.all())
        self.login_user(shopper.user)
        resp = self.remove_shopper(shopper)
        self.assertResponseIsPermissionDenied(resp)


class RequestedItemsViewTests(ViewTestCase):
    def setUp(self):
        super(RequestedItemsViewTests, self).setUp()

    def visit_requested_items(self):
        return self.get(reverse('core:requested-item-create'))

    def delete_requested_item(self, requested_item):
        return self.post(reverse('core:requested-item-delete', args=[requested_item.pk]))

    def claim_item(self, requested_item):
        return self.get(reverse('core:requested-item-claim', args=[requested_item.pk]))

    def view_requested_items(self):
        return self.get(reverse('core:requested-items'))

    def test_shopper_cannot_access_requesters_requested_items_list(self):
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        resp = self.view_requested_items()
        self.assertResponseIsPermissionDenied(resp)

    def test_requesters_can_access_requested_items_list(self):
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.view_requested_items()
        self.assertResponseOK(resp)

    def test_requesters_can_create_requested_items(self):
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.visit_requested_items()
        self.assertResponseOK(resp)

    def test_shoppers_cannot_create_requested_items(self):
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        resp = self.visit_requested_items()
        self.assertResponseIsPermissionDenied(resp)

    def test_owner_of_requested_item_can_delete(self):
        requested_item = test_utils.create_requested_item()
        requested_item_pk = requested_item.pk
        self.login_user(requested_item.requester.user)
        self.delete_requested_item(requested_item)
        self.assertFalse(RequestedItem.objects.filter(pk=requested_item_pk).exists())

    def test_other_requester_cannot_delete_requested_item(self):
        requested_item = test_utils.create_requested_item()
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.delete_requested_item(requested_item)
        self.assertResponseIsPermissionDenied(resp)

    def test_shopper_cannot_delete_requested_items(self):
        shopper = test_utils.create_shopper()
        requested_item = test_utils.create_requested_item()
        self.login_user(shopper.user)
        resp = self.delete_requested_item(requested_item)
        self.assertResponseIsPermissionDenied(resp)

    def test_shopper_can_claim_requested_item(self):
        shopper = test_utils.create_shopper()
        requested_item = test_utils.create_requested_item(shopper=shopper)
        self.login_user(shopper.user)
        self.claim_item(requested_item)
        requested_item.refresh_from_db()
        self.assertEqual(requested_item.shopper, shopper)

    def test_requester_cannot_claim_requested_item(self):
        requested_item = test_utils.create_requested_item()
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.claim_item(requested_item)
        self.assertResponseIsPermissionDenied(resp)

    def test_unauthorized_shopper_cannot_claim_requested_item(self):
        requested_item = test_utils.create_requested_item()
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        resp = self.claim_item(requested_item)
        self.assertResponseIsPermissionDenied(resp)


class CommentViewTests(ViewTestCase):
    def create_comment(self, requested_item, data):
        return self.post(reverse('core:comment-create', args=[requested_item.pk]), data=data)

    def delete_comment(self, comment):
        return self.post(reverse('core:comment-delete', args=[comment.pk]))

    def test_user_can_create_comment(self):
        comment_body = 'Bar'
        shopper = test_utils.create_shopper()
        requested_item = test_utils.create_requested_item(shopper=shopper)
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

    def test_unauthorized_user_cannot_create_comment(self):
        requested_item = test_utils.create_requested_item()
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.create_comment(requested_item, {'body': 'Foo'})
        self.assertResponseIsPermissionDenied(resp)

    def test_unauthorized_user_cannot_delete_comment(self):
        requested_item = test_utils.create_requested_item(shopper=test_utils.create_shopper())
        comment = test_utils.create_comment(requested_item=requested_item)
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.delete_comment(comment)

        self.assertResponseIsPermissionDenied(resp)


class ShopperViewTests(ViewTestCase):
    def view_shopper_detail(self, shopper):
        return self.get(reverse('core:shopper-detail', args=[shopper.pk]))

    def test_shoppers_cannot_can_view_shopper_list(self):
        shopper = test_utils.create_shopper()
        self.login_user(shopper.user)
        resp = self.client.get(reverse('core:shoppers'))
        self.assertResponseIsPermissionDenied(resp)

    def test_requester_cannot_view_unauthorized_shopper(self):
        requester = test_utils.create_requester()
        shopper = test_utils.create_shopper()
        self.login_user(requester.user)
        resp = self.view_shopper_detail(shopper)
        self.assertResponseIsPermissionDenied(resp)

    def test_shopper_cannot_view_shopper_detail(self):
        shopper_one = test_utils.create_shopper()
        shopper_two = test_utils.create_shopper()
        self.login_user(shopper_one.user)
        resp = self.view_shopper_detail(shopper_two)
        self.assertResponseIsPermissionDenied(resp)


class RequestersForShopperViewTests(ViewTestCase):
    def view_requester_detail(self, requester):
        return self.get(reverse('core:requester-detail', args=[requester.pk]))

    def test_requester_cannot_view_requesters_for_shopper(self):
        requester = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.get(reverse('core:requesters'))
        self.assertResponseIsPermissionDenied(resp)

    def test_requester_cannot_view_requester_detail(self):
        requester = test_utils.create_requester()
        requester_two = test_utils.create_requester()
        self.login_user(requester.user)
        resp = self.view_requester_detail(requester_two)
        self.assertResponseIsPermissionDenied(resp)

    def test_shopper_cannot_view_detail_of_unauthorized_requester(self):
        shopper = test_utils.create_shopper()
        requester = test_utils.create_requester()
        self.login_user(shopper.user)
        resp = self.view_requester_detail(requester)
        self.assertResponseIsPermissionDenied(resp)
