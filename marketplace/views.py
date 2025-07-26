from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch
from django.views.decorators.http import require_GET
from vendor.models import Vendor
from menu.models import Category, FoodItem
from marketplace.models import Cart
from marketplace.context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required
from decimal import Decimal
# Create your views here.


def marketplace(request):
    """
    View function to display a list of approved and active vendors in the marketplace.

    Retrieves all Vendor objects that are both approved and whose associated user accounts are active.
    Counts the number of such vendors and passes both the queryset and the count to the template context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML page displaying the list of vendors and their count.
    """
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, slug):
    """
    View function to display the details of a specific vendor.
    Retrieves the vendor object based on the provided slug. Fetches all categories associated with the vendor,
    prefetching related available food items for efficiency. If the user is authenticated, retrieves their cart items;
    otherwise, sets cart items to None. Renders the 'marketplace/detail.html' template with the vendor, categories,
    and cart items in the context.
    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug identifier for the vendor.
    Returns:
        HttpResponse: The rendered detail page for the vendor.
    """
    vendor = get_object_or_404(Vendor, slug=slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'cart_items': cart_items,
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'marketplace/detail.html', context)


@require_GET  # Ensures this view only responds to GET requests
def add_to_cart(request, food_id):
    """
    Handles adding a food item to the authenticated user's cart via an AJAX request.
    Parameters:
        request (HttpRequest): The HTTP request object. Must be an authenticated user and an AJAX request.
        food_id (int): The ID of the FoodItem to add to the cart.
    Returns:
        JsonResponse: A JSON response indicating the result of the operation:
            - If successful, returns status 'success', a message, updated cart counter, and item quantity.
            - If the food item does not exist, returns status 'failed' and an error message.
            - If the request is invalid (not AJAX), returns status 'failed' and an error message.
            - If the user is not authenticated, returns status 'login_required' and a login prompt message.
    Raises:
        FoodItem.DoesNotExist: If the specified food item does not exist in the database.
    """
    if request.user.is_authenticated:
        # More reliable than is_ajax (deprecated)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Checks if the food item exists
                fooditem = FoodItem.objects.get(id=food_id)

                # Checks if the item already exists in the user's cart
                cart_item, created = Cart.objects.get_or_create(
                    user=request.user,
                    fooditem=fooditem,
                    defaults={'quantity': 1}
                )

                if not created:
                    # Item already in cart, increment quantity
                    cart_item.quantity += 1
                    cart_item.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Increased the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'cart_amounts': get_cart_amounts(request),
                        'qty': cart_item.quantity,
                    })
                else:
                    # New item added to cart
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Food added to cart successfully',
                        'cart_counter': get_cart_counter(request),
                        'cart_amounts': get_cart_amounts(request),
                        'qty': cart_item.quantity,
                    })

            except FoodItem.DoesNotExist:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'This food item does not exist.',
                })

        return JsonResponse({
            'status': 'failed',
            'message': 'Invalid request.',
        })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please log in to continue. Redirecting...',
        })


@require_GET
def decrease_cart(request, food_id):
    """
    Handles AJAX requests to decrease the quantity of a specific food item in the authenticated user's cart.
    If the quantity of the item is greater than one, it decrements the quantity by one and updates the cart.
    If the quantity is one, it removes the item from the cart.
    Returns a JSON response indicating the status, updated cart counter, and current quantity.
    Handles cases where the food item or cart item does not exist, or if the request is invalid or unauthenticated.
    Args:
        request (HttpRequest): The HTTP request object.
        food_id (int): The ID of the food item to decrease in the cart.
    Returns:
        JsonResponse: A JSON response with the operation status, updated cart counter, and quantity.
    """
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = get_object_or_404(FoodItem, id=food_id)
                try:
                    cart_item = Cart.objects.get(
                        user=request.user, fooditem=fooditem)

                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                        return JsonResponse({
                            'status': 'success',
                            'cart_counter': get_cart_counter(request),
                            'cart_amounts': get_cart_amounts(request),
                            'qty': cart_item.quantity,
                        })
                    else:
                        cart_item.delete()
                        return JsonResponse({
                            'status': 'success',
                            'cart_counter': get_cart_counter(request),
                            'cart_amounts': get_cart_amounts(request),
                            'qty': 0,
                        })

                except Cart.DoesNotExist:
                    return JsonResponse({
                        'status': 'failed',
                        'message': f'"{fooditem.food_title}" is not in your cart.'
                    })

            except FoodItem.DoesNotExist:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Food item not found.'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request.',
            })
    return JsonResponse({
        'status': 'login_required',
        'message': 'Please log in to continue. Redirecting...',
    })


@login_required(login_url='login')
def cart(request):

    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


@require_GET
def remove_from_cart(request, cart_id):
    """
    Removes an item from the authenticated user's cart.

    Handles AJAX requests to remove a specific cart item by its ID. 
        Only processes requests from authenticated users and expects the request 
        to be made via XMLHttpRequest. Returns a JSON response indicating the result
        of the operation, including updated cart counter information if successful.

    Args:
        request (HttpRequest): The HTTP request object.
        cart_id (int): The ID of the cart item to be removed.

    Returns:
        JsonResponse: A JSON response containing the status of the operation, 
            a message, and optionally the updated cart counter.

    Possible status values:
        - 'success': Item was removed successfully.
        - 'failed': The request was invalid or the cart item does not exist.
        - 'login_required': The user is not authenticated.
    """
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(id=cart_id, user=request.user)
                cart_item.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item removed from cart successfully',
                    'cart_counter': get_cart_counter(request),
                    'cart_amounts': get_cart_amounts(request),
                })
            except Cart.DoesNotExist:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Cart item does not exist.'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request.',
            })
    return JsonResponse({
        'status': 'login_required',
        'message': 'Please log in to continue. Redirecting...',
    })
