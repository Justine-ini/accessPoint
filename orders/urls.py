from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order-complete/', views.order_complete, name='order_complete'),
    path("order/receipt/", views.download_receipt, name="download_receipt"),
]
