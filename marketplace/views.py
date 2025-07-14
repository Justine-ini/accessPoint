from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch
from django.views.decorators.http import require_GET
from vendor.models import Vendor
from menu.models import Category, FoodItem
from marketplace.models import Cart
from marketplace.context_processors import get_cart_counter
# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, slug):
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
                        'qty': cart_item.quantity,
                    })
                else:
                    # New item added to cart
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Food added to cart successfully',
                        'cart_counter': get_cart_counter(request),
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


@require_GET  # Ensures this view only responds to GET requests
@require_GET
def decrease_cart(request, food_id):
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
                            'qty': cart_item.quantity,
                        })
                    else:
                        cart_item.delete()
                        return JsonResponse({
                            'status': 'success',
                            'cart_counter': get_cart_counter(request),
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


# @login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    context = {
        'cart_items': cart_items
    }
    return render(request, 'marketplace/cart.html', context)
