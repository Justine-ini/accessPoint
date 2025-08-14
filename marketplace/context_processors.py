from decimal import Decimal
from django.db import DatabaseError
from .models import Cart, Tax
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
    tax = Decimal('0')
    total = Decimal('0')
    subtotal = Decimal('0')
    tax_dict = {}

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items.exists():
            for item in cart_items:
                fooditem = FoodItem.objects.get(pk=item.fooditem.id)
                subtotal += Decimal(fooditem.price) * Decimal(item.quantity)

            get_tax = Tax.objects.filter(is_active=True)

            # Convert all keys and values to strings
            tax_dict = {
                str(tax.tax_type): {
                    str(tax.tax_percentage): str(round(
                        (Decimal(tax.tax_percentage) / Decimal(100)) * subtotal, 2))
                }
                for tax in get_tax
            }

            tax = sum(Decimal(amount) for d in tax_dict.values()
                      for amount in d.values())

            total = subtotal + tax
    print(tax_dict)
    return {
        'cart_subtotal': str(subtotal),
        'cart_tax': str(tax),
        'cart_total': str(total),
        'tax_dict': tax_dict,  # Already converted to strings
    }
