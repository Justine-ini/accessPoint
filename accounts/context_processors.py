from vendor.models import Vendor
from .models import UserProfile
from django.conf import settings


def get_vendor(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            vendor = None
    else:
        vendor = None

    return dict(vendor=vendor)


def get_user_profile(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None

    return dict(user_profile=user_profile)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}
