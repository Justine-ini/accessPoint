from .models import Cart
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items.exists():
                cart_count = sum(item.quantity for item in cart_items)
            else:
                cart_count = 0
        except:
            cart_count = 0
    return {'cart_count': cart_count}
