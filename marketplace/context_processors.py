from django.db import DatabaseError
from .models import Cart
from marketplace.models import FoodItem


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


def get_cart_amounts(request):
    tax = 0
    total = 0
    subtotal = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items.exists():
            for item in cart_items:
                fooditem = FoodItem.objects.get(pk=item.fooditem.id)
                subtotal += fooditem.price * item.quantity
            total = subtotal + tax
    return {
        'cart_subtotal': subtotal,
        'cart_tax': tax,
        'cart_total': total
    }
