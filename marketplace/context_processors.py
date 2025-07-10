from django.db import DatabaseError
from .models import Cart


def get_cart_counter(request):
    """
    Context processor to calculate the total quantity of items in the authenticated user's cart.

    Args:
        request (HttpRequest): The HTTP request object containing user information.

    Returns:
        dict: A dictionary with the key 'cart_count' representing the total quantity 
        of items in the user's cart.
        If the user is not authenticated or an error occurs, 'cart_count' will be 0.
    """
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items.exists():
                cart_count = sum(item.quantity for item in cart_items)
            else:
                cart_count = 0
        except DatabaseError:
            cart_count = 0
    return {'cart_count': cart_count}
