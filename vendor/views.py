from django.shortcuts import render, get_object_or_404, redirect
from accounts.forms import UserProfileForm
from .models import Vendor
from menu.models import Category, FoodItem
from .forms import VendorForm
from menu.forms import CategoryForm, FoodItemForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import vendor_restrict
from django.utils.text import slugify


# Create your views here.
def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated successfully!.')
            return redirect('vendor_profile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }

    return render(request, 'vendors/vendor_profile.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendors/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'category': category,
        'fooditems': fooditems,
    }
    return render(request, 'vendors/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            vendor = get_vendor(request)
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = slugify(category.category_name)
            category.save()

            messages.success(request, 'Category saved successfully!')
            return redirect('menu_builder')
        else:
            pass
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }
    return render(request, 'vendors/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def add_fooditem(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = get_vendor(request)
            fooditem = form.save(commit=False)
            fooditem.vendor = vendor
            fooditem.slug = slugify(fooditem.food_title)
            fooditem.save()

            messages.success(request, 'Food Item saved successfully!')
            return redirect('menu_builder')
        else:
            messages.error(request, 'There was a problem saving the category.')
            return redirect('add_fooditem')

    else:
        form = FoodItemForm()

    context = {
        'form': form,
    }

    return render(request, 'vendors/add_fooditem.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            vendor = get_vendor(request)
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = slugify(category.category_name)
            category.save()

            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            pass
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendors/edit_category.html', context)


def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.info(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')
