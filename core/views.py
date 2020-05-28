from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from core.models import RequestedItem, Shopper, Requester


class RequestedItemsListView(LoginRequiredMixin, ListView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_list.html'

    def get_queryset(self):
        return RequestedItem.objects.for_user(self.request.user)


class RequestedItemsCreateView(LoginRequiredMixin, CreateView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_create.html'
    fields = ['item', 'quantity', 'priority']

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

    def get_queryset(self):
        return RequestedItem.objects.for_user(self.request.user)


class RequestedItemsDeleteView(LoginRequiredMixin, DeleteView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_delete.html'

    def get_success_url(self):
        return reverse('core:requested-items')


class RequestedItemsUpdateView(LoginRequiredMixin, UpdateView):
    model = RequestedItem
    template_name = 'core/requested_item/requested_item_update.html'
    fields = ['quantity', 'priority', 'shopper']

    def get_success_url(self):
        return reverse('core:requested-item-detail', args=[self.object.pk])


class RequestedItemsClaimView(LoginRequiredMixin, SingleObjectMixin, View):
    model = RequestedItem

    def get(self, request, pk, *args, **kwargs):
        shopper = get_object_or_404(Shopper, user=self.request.user)
        requested_item = self.get_object()
        shopper.claim_requested_item(requested_item)
        return redirect('core:requester-detail', pk=requested_item.requester.pk)


class AddShopperView(LoginRequiredMixin, View):
    model = Requester

    def get(self, request, pk, invite_token, *args, **kwargs):
        shopper = get_object_or_404(Shopper, user=self.request.user)
        requester = get_object_or_404(Requester, pk=pk, invite_token=invite_token)
        requester.add_shopper(shopper)
        return redirect('account_login')


class RemoveShopperView(LoginRequiredMixin, View):
    model = Requester

    def get(self, request, shopper_pk, *args, **kwargs):
        requester = get_object_or_404(Requester, user=self.request.user)
        shopper = get_object_or_404(Shopper, pk=shopper_pk)
        requester.remove_shopper(shopper)
        return redirect('core:shoppers')


class ShoppersListView(LoginRequiredMixin, ListView):
    model = Shopper
    template_name = 'core/shopper/shoppers_list.html'

    def get_queryset(self):
        return Requester.objects.get(user=self.request.user).shoppers.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ShoppersListView, self).get_context_data(**kwargs)
        context['requester'] = Requester.objects.get(user=self.request.user)
        return context


class ShoppersDetailView(LoginRequiredMixin, DetailView):
    model = Shopper
    template_name = 'core/shopper/shopper_detail.html'
    context_object_name = 'shopper'

    def get_queryset(self):
        return Requester.objects.get(user=self.request.user).shoppers.all()


class RequesterForShopperListView(LoginRequiredMixin, ListView):
    model = Requester
    template_name = 'core/requester/requesters_for_shopper_list.html'

    def get_queryset(self):
        return Shopper.objects.get(user=self.request.user).requesters.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RequesterForShopperListView, self).get_context_data(**kwargs)
        context['shopper'] = Shopper.objects.get(user=self.request.user)
        return context


class RequesterForShopperDetailView(LoginRequiredMixin, DetailView):
    model = Requester
    template_name = 'core/requester/requester_for_shopper_detail.html'
    context_object_name = 'requester'

    def get_queryset(self):
        return Shopper.objects.get(user=self.request.user).requesters.all()
