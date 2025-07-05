from django.shortcuts import render
from vendor.models import Vendor


def home(request):
    """
    Renders the home page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'home.html' template.
    """
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)
