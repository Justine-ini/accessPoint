from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from accounts.models import UserProfile
from accounts.forms import UserProfileForm
from accounts.views import vendor_restrict
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from .forms import VendorForm
from .models import Vendor


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
        'vendor_profile_active': request.path.startswith('/vendor/profile/')
    }

    return render(request, 'vendors/vendor_profile.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
        'menu_builder_active': request.path.startswith('/vendor/menu-builder/'),
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


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.info(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def add_fooditem(request):
    vendor = get_vendor(request)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            fooditem = form.save(commit=False)
            fooditem.food_title = fooditem.food_title.capitalize()
            fooditem.vendor = vendor
            fooditem.slug = slugify(fooditem.food_title)
            try:
                fooditem.save()
                messages.success(request, 'Food Item saved successfully!')
                return redirect('fooditems_by_category', fooditem.category.id)
            except IntegrityError:
                form.add_error(
                    'food_title', "A food item with this name already exists.")
        else:
            pass
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(
            vendor=vendor)

    context = {
        'form': form,
    }

    return render(request, 'vendors/add_fooditem.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def edit_fooditem(request, pk=None):
    vendor = get_vendor(request)
    fooditem = get_object_or_404(FoodItem, pk=pk)

    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=fooditem)
        if form.is_valid():

            foodtitle = form.cleaned_data['food_title']
            item = form.save(commit=False)
            item.vendor = vendor
            # You could also move this logic to models.py
            item.slug = slugify(foodtitle)
            item.save()

            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_category', item.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=fooditem)
        form.fields['category'].queryset = Category.objects.filter(
            vendor=vendor)

    context = {
        'form': form,
        'fooditem': fooditem,
    }
    return render(request, 'vendors/edit_fooditem.html', context)


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def delete_fooditem(request, pk=None):
    """
    Delete a food item by its primary key and redirect to the food items list for its category.
    """
    fooditem = get_object_or_404(FoodItem, pk=pk)
    fooditem.delete()
    messages.info(request, 'Food Item has been deleted successfully!')
    return redirect('fooditems_by_category', fooditem.category.id)
