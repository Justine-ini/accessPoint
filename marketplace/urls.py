from django.urls import path
from .import views
urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:slug>/', views.vendor_detail, name='vendor_detail'),

    # Add to cart
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # Decrease cart
    path('decrease-cart/<int:food_id>/',
         views.decrease_cart, name='decrease_cart'),
    # Remove from cart
    path('remove-from-cart/<int:cart_id>/',
         views.remove_from_cart, name='remove_from_cart'),
]
