from django.urls import path
from accounts import views as AccountViews
from .import views

urlpatterns = [
    path('', AccountViews.customer_dashboard, name='customer_dashboard'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('my-orders/', views.my_orders, name='customer_my_orders'),
    path('order-detail/<str:order_number>/', views.order_detail,
         name='order_detail'),

]
