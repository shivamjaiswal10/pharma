from django.urls import path
from . import views
from .views import (
    ItemDetailView,
    CheckoutView,
    #HomeView,
    home,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    SearchResultsView,
    upload_prescription,
    AccountSetting,
    OrderHistory
)

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
   # path('demo2/', autocomplete1, name='autocomplete1'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('upload_prescription/', upload_prescription.as_view(), name='upload_prescription'),
    path('account_setting/', AccountSetting.as_view(), name='account_setting'),
    path('order_history/', OrderHistory.as_view(), name='order_history')
]
