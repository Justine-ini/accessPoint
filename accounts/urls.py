from django.urls import path
from .import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('registerUser/', views.register_user, name='registerUser'),
    path('registerVendor/', views.register_vendor, name='registerVendor'),

    path('my-account/', views.my_account, name='myAccount'),

    path('customer-dashboard/', views.customer_dashboard,
         name='customer-dashboard'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor-dashboard'),

    path('activate/<uidb64>/<token>/',
         views.activate, name='activate'),
]
