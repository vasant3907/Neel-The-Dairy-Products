# URLs (urls.py)
from django.urls import path
from .views import RegisterAPI, LoginAPI, HomeAPI
from django.urls import path
from .views import *



urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('home/', HomeAPI.as_view(), name='home'),
    
    # Product
    path('products/', ProductListCreateAPI.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDeleteAPI.as_view(), name='product-detail'),

    # Customer
    path('customers/', CustomerListCreateAPI.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerRetrieveUpdateDeleteAPI.as_view(), name='customer-detail'),

    # Cart
    path('carts/', CartListCreateAPI.as_view(), name='cart-list-create'),
    path('carts/<int:pk>/', CartRetrieveUpdateDeleteAPI.as_view(), name='cart-detail'),

    # # Payment
    path('payments/', PaymentListCreateAPI.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentRetrieveUpdateDeleteAPI.as_view(), name='payment-detail'),

    # # Order
    path('orders/', OrderPlacedListCreateAPI.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderPlacedRetrieveUpdateDeleteAPI.as_view(), name='order-detail'),

    # Wishlist
    path('wishlists/', WishlistListCreateAPI.as_view(), name='wishlist-list-create'),
    path('wishlists/<int:pk>/', WishlistRetrieveUpdateDeleteAPI.as_view(), name='wishlist-detail'),
    
    path('api/payments/create-intent/', CreateStripePaymentIntentAPI.as_view(), name='create-payment-intent'),
    path('api/payments/verify/', VerifyStripePaymentAPI.as_view(), name='verify-payment'),
   

    path("reviews/", ReviewListCreateAPI.as_view(), name="review-list-create"),
    path("reviews/<int:pk>/", ReviewRetrieveUpdateDeleteAPI.as_view(), name="review-detail"),
    
    # Stock APIs (if you want to expose stock info)
    path('stocks/', StockListAPI.as_view(), name='stock-list'),
    path('stocks/<int:product__id>/', StockDetailAPI.as_view(), name='stock-detail'),
]