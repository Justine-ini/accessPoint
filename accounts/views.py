"""Views for user registration and management."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from vendor.forms import VendorForm
from .forms import UserForm, LoginForm
from .models import User, UserProfile
from .utils import get_user_role, vendor_restrict, customer_restrict


def register_user(request):
    """Handle user registration with form validation and account creation."""
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('myAccount')
    elif request.method == 'POST':
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
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('myAccount')
    elif request.method == 'POST':
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


def login_user(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email').strip().lower()
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f'Welcome back, {user.get_full_name()}!')
                return redirect('myAccount')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    context = {
        'form': form
    }

    return render(request, 'accounts/login.html', context)


@login_required(login_url='login')
def logout_user(request):
    """Handle user logout and clear messages."""

    logout(request)
    # Clear all existing messages
    storage = messages.get_messages(request)
    for message in storage:
        pass

    # Add logout message
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def my_account(request):
    user = request.user
    redirect_url = get_user_role(user)
    return redirect(redirect_url)


@login_required(login_url='login')
@user_passes_test(customer_restrict)
def customer_dashboard(request):
    return render(request, 'accounts/customer_dashboard.html')


@login_required(login_url='login')
@user_passes_test(vendor_restrict)
def vendor_dashboard(request):
    return render(request, 'accounts/vendor_dashboard.html')
