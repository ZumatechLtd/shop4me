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


class AddShopperView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Requester
    slug_field = 'invite_token'
    slug_url_kwarg = 'invite_token'

    def get(self, request, *args, **kwargs):
        shopper = get_object_or_404(Shopper, user=self.request.user)
        requester = self.get_object()
        requester.add_shopper(shopper)
        return redirect('account_login')
