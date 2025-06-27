from vendor.models import Vendor
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


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}
