from vendor.models import Vendor
from .models import UserProfile
from django.conf import settings


def get_vendor(request):
    """
    Context processor that retrieves the Vendor instance associated with the authenticated user.
    Args:
        request (HttpRequest): The current HTTP request object.
    Returns:
        dict: A dictionary containing the 'vendor' key mapped to the Vendor instance if the 
            user is authenticated and associated with a Vendor, otherwise None.
    """
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            vendor = None
    else:
        vendor = None

    return dict(vendor=vendor)


def get_user_profile(request):
    """
    Context processor that adds the authenticated user's profile to the template context.
    Args:
        request (HttpRequest): The current HTTP request object.
    Returns:
        dict: A dictionary containing the user's profile under the key 'user_profile'.
              If the user is not authenticated or the profile does not exist, the value is None.
    """
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None
    else:
        user_profile = None

    return dict(user_profile=user_profile)


def get_google_api(request):
    """
    Context processor that adds the Google API key to the template context.

    Args:
        request(HttpRequest): The current HTTP request object.

    Returns:
        dict: A dictionary containing the Google API key under the key 'GOOGLE_API_KEY'.
    """
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}


def paystack_public_key(request):
    """
    Context processor that adds the PAYSTACK PUBLIC KEY to the template context.

    Args:
        request(HttpRequest): The current HTTP request object.

    Returns:
        dict: A dictionary containing the Paystack Public Key under the key 'PAYSTACK_PUBLIC_KEY'.
    """
    return {
        'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY,
    }
