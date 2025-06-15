"""Views for user registration and management."""
from django.shortcuts import render, redirect
from django.contrib import messages
from vendor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile


def register_user(request):
    """Handle user registration with form validation and account creation."""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create user object without saving
            user = form.save(commit=False)

            # Apply cleaned data transformations
            user.first_name = form.cleaned_data['first_name'].strip().title()
            user.last_name = form.cleaned_data['last_name'].strip().title()
            user.email = form.cleaned_data['email'].strip().lower()

            # Hash password securely
            user.set_password(form.cleaned_data['password'])
            user.role = User.CUSTOMER
            user.save()

            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserForm()
    context = {
        'form': form,
    }

    return render(request, 'accounts/registerUser.html', context)


def register_vendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            # Create user object without saving
            user = form.save(commit=False)

            # Apply cleaned data transformations
            user.first_name = form.cleaned_data['first_name'].strip().title()
            user.last_name = form.cleaned_data['last_name'].strip().title()
            user.email = form.cleaned_data['email'].strip().lower()

            # Hash password securely
            user.set_password(form.cleaned_data['password'])
            user.role = User.VENDOR
            user.save()

            # Create vendor profile
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Vendor account created successfully!')
            return redirect('home')
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context)
