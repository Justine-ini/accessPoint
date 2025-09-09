from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from orders.models import Order, OrderedFood
from django.core.paginator import Paginator


@login_required(login_url='login')
def customer_profile(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=request.user)
    profile_form = UserProfileForm(instance=profile)
    user_form = UserInfoForm(instance=user)

    if request.method == 'POST':
        # bind POST data (and files for picture/avatar) to the forms using instance
        user_form = UserInfoForm(request.POST, instance=user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user  # ensure relation if not already set
            profile.save()

            messages.success(request, "Profile updated successfully.")
            return redirect('customer_profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # GET — prepopulate forms from existing instances
        user_form = UserInfoForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'customer_profile_active': request.resolver_match.url_name == 'customer_profile',
    }
    return render(request, 'customers/customer_profile.html', context)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')

    paginator = Paginator(orders, 10)   # 10 orders per page
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        # keep backward-compatibility if other code expects 'orders' variable:
        'orders': page_obj.object_list,
        'order_count': orders.count(),
        'customer_my_orders_active': request.resolver_match.url_name == 'customer_my_orders',
    }
    return render(request, 'customers/my_orders.html', context)


@login_required(login_url='login')
def order_detail(request, order_number):
    try:
        order = get_object_or_404(
            Order, order_number=order_number, user=request.user, is_ordered=True)
        ordered_foods = OrderedFood.objects.filter(order=order)
    except Order.DoesNotExist:
        return redirect('customer')

    subtotal = sum(item.amount for item in ordered_foods)

    context = {
        "subtotal": subtotal,
        'order': order,
        'ordered_foods': ordered_foods,
    }
    return render(request, 'customers/order_detail.html', context)
