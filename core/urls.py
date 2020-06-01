from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('requested-items/', views.RequestedItemsListView.as_view(), name='requested-items'),
    path('requested-item/new/', views.RequestedItemsCreateView.as_view(), name='requested-item-create'),
    path('requested-item/<int:pk>/', views.RequestedItemsDetailView.as_view(), name='requested-item-detail'),
    path('requested-item/<int:pk>/delete/', views.RequestedItemsDeleteView.as_view(), name='requested-item-delete'),
    path('requested-item/<int:pk>/update/', views.RequestedItemsUpdateView.as_view(), name='requested-item-update'),
    path('requested-item/<int:pk>/claim/', views.RequestedItemsClaimView.as_view(), name='requested-item-claim'),

    path('shoppers/', views.ShoppersListView.as_view(), name='shoppers'),
    path('shopper/<int:pk>/', views.ShoppersDetailView.as_view(), name='shopper-detail'),

    path('requesters/', views.RequesterForShopperListView.as_view(), name='requesters'),
    path('requester/<int:pk>/', views.RequesterForShopperDetailView.as_view(), name='requester-detail'),

    path('add-shopper/<int:pk>/<str:invite_token>/', views.AddShopperView.as_view(), name='add-shopper'),
    path('remove-shopper/<int:pk>/', views.RemoveShopperView.as_view(), name='remove-shopper'),

    path('requested-item/<int:pk>/comment/new/', views.CommentCreateView.as_view(), name='comment-create'),
    path('requested-item/comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
]
