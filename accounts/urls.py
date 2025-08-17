from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.my_account, name='myAccount'),

    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('registerUser/', views.register_user, name='registerUser'),
    path('registerVendor/', views.register_vendor, name='registerVendor'),

    path('my-account/', views.my_account, name='myAccount'),

    path('customer-dashboard/', views.customer_dashboard,
         name='customer-dashboard'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor-dashboard'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password-validate/<uidb64>/<token>/',
         views.reset_password_validate, name='reset_password_validate'),
    path('reset-password-done/', views.reset_password_done,
         name='reset_password_done'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls')),
]
