from django.urls import path
from accounts import views as AccountViews
from .import views

urlpatterns = [
    path('', AccountViews.vendor_dashboard, name='vendor-dashboard'),
    path('profile/', views.vendor_profile, name='vendor_profile'),
]
