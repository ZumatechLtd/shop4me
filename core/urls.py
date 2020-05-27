from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('requested-items/', views.RequestedItemsListView.as_view(), name='requested-items'),
    path('requested-item/new/', views.RequestedItemsCreateView.as_view(), name='requested-item-create'),
    path('requested-item/<int:pk>/', views.RequestedItemsDetailView.as_view(), name='requested-item-detail'),
    path('requested-item/<int:pk>/delete/', views.RequestedItemsDeleteView.as_view(), name='requested-item-delete'),
    path('requested-item/<int:pk>/update/', views.RequestedItemsUpdateView.as_view(), name='requested-item-update'),

    path('add-shopper/<int:pk>/<str:invite_token>/', views.AddShopperView.as_view(), name='add-shopper'),

]
