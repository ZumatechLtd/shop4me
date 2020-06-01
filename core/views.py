from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from core.models import RequestedItem, Shopper, Requester, Comment, Profile


class UserTestMixin(LoginRequiredMixin, UserPassesTestMixin):
    tests = []

    def test_func(self):
        return all([f(self) for f in self.tests])


def user_is_requester(view_cls):
    return Profile.user_is_requester(view_cls.request.user)


def user_is_shopper(view_cls):
    return Profile.user_is_shopper(view_cls.request.user)


def requester_owns_requested_item(view_cls):
    return user_is_requester(view_cls) and RequestedItem.objects.filter(pk=view_cls.kwargs[view_cls.pk_url_kwarg], requester=view_cls.request.user.requester).exists()


def user_is_authorized_shopper(view_cls):
    requested_item = RequestedItem.objects.get(pk=view_cls.kwargs[view_cls.pk_url_kwarg])
    requester = requested_item.requester
    return user_is_shopper(view_cls) and view_cls.request.user.shopper in requester.shoppers.all()


def shopper_is_authorized_for_requester(view_cls):
    return user_is_requester(view_cls) and view_cls.kwargs['pk'] in view_cls.request.user.requester.shoppers.all().values_list('id', flat=True)


def requester_is_authorized_for_shopper(view_cls):
    return user_is_shopper(view_cls) and view_cls.kwargs['pk'] in view_cls.request.user.shopper.requesters.all().values_list('id', flat=True)


def user_is_authorized_on_requested_item(view_cls):
    requested_item = RequestedItem.objects.get(pk=view_cls.kwargs['pk'])
    authorized_users = [requested_item.requester.user]
    if requested_item.shopper is not None:
        authorized_users.append(requested_item.shopper.user)
    return view_cls.request.user in authorized_users


def comment_belongs_to_user(view_cls):
    return view_cls.request.user == view_cls.model.objects.get(pk=view_cls.kwargs[view_cls.pk_url_kwarg]).author


class IndexView(TemplateView):
    template_name = 'core/index.html'


class RequestedItemsListView(UserTestMixin, ListView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_list.html'
    tests = [user_is_requester]

    def get_queryset(self):
        return RequestedItem.objects.for_user(self.request.user)


class RequestedItemsCreateView(UserTestMixin, CreateView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_create.html'
    fields = ['item', 'quantity', 'priority']
    tests = [user_is_requester]

    def get_success_url(self):
        return reverse('core:requested-item-detail', args=[self.object.id])

    def form_valid(self, form):
        form.instance.requester = self.request.user.requester
        form.instance.save()
        return super().form_valid(form)


class RequestedItemsDetailView(LoginRequiredMixin, DetailView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_detail.html'
    context_object_name = 'requested_item'


class RequestedItemsDeleteView(UserTestMixin, DeleteView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_delete.html'
    tests = [requester_owns_requested_item]

    def get_success_url(self):
        return reverse('core:requested-items')


class RequestedItemsUpdateView(UserTestMixin, UpdateView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_update.html'
    fields = ['quantity', 'priority', 'shopper']
    tests = [requester_owns_requested_item]

    def get_success_url(self):
        return reverse('core:requested-item-detail', args=[self.object.pk])


class RequestedItemsClaimView(UserTestMixin, SingleObjectMixin, View):
    model = RequestedItem
    tests = [user_is_shopper, user_is_authorized_shopper]

    def get(self, request, pk, *args, **kwargs):
        shopper = get_object_or_404(Shopper, user=self.request.user)
        requested_item = self.get_object()
        shopper.claim_requested_item(requested_item)
        return redirect('core:requester-detail', pk=requested_item.requester.pk)


class AddShopperView(UserTestMixin, View):
    model = Requester
    tests = [user_is_shopper]

    def get(self, request, pk, invite_token, *args, **kwargs):
        shopper = get_object_or_404(Shopper, user=self.request.user)
        requester = get_object_or_404(Requester, pk=pk, invite_token=invite_token)
        requester.add_shopper(shopper)
        return redirect('account_login')


class RemoveShopperView(UserTestMixin, View):
    model = Requester
    tests = [shopper_is_authorized_for_requester]

    def get(self, request, pk, *args, **kwargs):
        requester = get_object_or_404(Requester, user=self.request.user)
        shopper = get_object_or_404(Shopper, pk=pk)
        requester.remove_shopper(shopper)
        return redirect('core:shoppers')


class ShoppersListView(UserTestMixin, ListView):
    model = Shopper
    template_name = 'core/shopper/shoppers_list.html'
    tests = [user_is_requester]

    def get_queryset(self):
        return Requester.objects.get(user=self.request.user).shoppers.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ShoppersListView, self).get_context_data(**kwargs)
        context['requester'] = Requester.objects.get(user=self.request.user)
        return context


class ShoppersDetailView(UserTestMixin, DetailView):
    model = Shopper
    template_name = 'core/shopper/shopper_detail.html'
    context_object_name = 'shopper'
    tests = [shopper_is_authorized_for_requester]

    def get_queryset(self):
        return Requester.objects.get(user=self.request.user).shoppers.all()


class RequesterForShopperListView(UserTestMixin, ListView):
    model = Requester
    template_name = 'core/requester/requesters_for_shopper_list.html'
    tests = [user_is_shopper]

    def get_queryset(self):
        return Shopper.objects.get(user=self.request.user).requesters.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RequesterForShopperListView, self).get_context_data(**kwargs)
        context['shopper'] = Shopper.objects.get(user=self.request.user)
        return context


class RequesterForShopperDetailView(UserTestMixin, DetailView):
    model = Requester
    template_name = 'core/requester/requester_for_shopper_detail.html'
    context_object_name = 'requester'
    tests = [requester_is_authorized_for_shopper]

    def get_queryset(self):
        return Shopper.objects.get(user=self.request.user).requesters.all()


class CommentCreateView(UserTestMixin, CreateView):
    model = Comment
    template_name = 'core/comment/comment_create.html'
    fields = ['body']
    tests = [comment_belongs_to_user]

    def get_success_url(self):
        return reverse('core:requested-item-detail', args=[self.kwargs['pk']])

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.requested_item_id = self.kwargs['pk']
        return super(CommentCreateView, self).form_valid(form)


class CommentDeleteView(UserTestMixin, DeleteView):
    model = Comment
    template_name = 'core/comment/comment_delete.html'
    tests = [comment_belongs_to_user]

    def get_success_url(self):
        return reverse('core:requested-item-detail', args=[self.object.requested_item.pk])
