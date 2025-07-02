"""Views for user registration and management."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from vendor.forms import VendorForm
from .forms import UserForm, LoginForm
from .models import User, UserProfile
from .utils import get_user_role, vendor_restrict, customer_restrict, send_verification_email


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

            # Send verification email
            mail_subject = 'Verify your email address for your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            # Alert messages
            messages.success(
                request, 'Account created successfully! Please check your email to activate your account.')
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form,
    }

    return render(request, 'accounts/registerUser.html', context)


def register_vendor(request):
    """Handle vendor registration with form validation, account creation, and email verification"""

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

            # Send verification email
            mail_subject = 'Activate your vendor account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            # Clear the form data after successful registration
            form = UserForm()

            messages.success(
                request, 'Vendor account created successfully! Please check your email to activate your account.')
            return redirect('home')
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context)


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Your account has been activated successfully!')
        return redirect('myAccount')
    messages.error(request, 'Activation link is invalid or has expired.')
    return redirect('myAccount')


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
    context = {
        'dashboard_active': request.path == '/vendor-dashboard/' or request.path == '/vendor/'
    }
    return render(request, 'accounts/vendor_dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'accounts/forgot_password.html')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(
                request, 'No account found with that email address.')
            return render(request, 'accounts/forgot_password.html')

        if not user.is_active:
            messages.error(
                request, 'Your account is inactive. Please contact support.')
            return render(request, 'accounts/forgot_password.html')

        # Send password reset email
        mail_subject = 'Reset your password'
        email_template = 'accounts/emails/reset_password_email.html'
        send_verification_email(request, user, mail_subject, email_template)
        messages.success(
            request, 'Password reset link has been sent to your email.')
        return render(request, 'accounts/forgot_password.html')
    else:
        # Render the forgot password page
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('myAccount')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        # messages.info(request, 'Please reset your password.')
        return redirect('reset_password_done')
    else:
        messages.error(
            request, 'The password reset link is invalid or has expired.')
        return redirect('myAccount')


def reset_password_done(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if not password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
            return redirect('reset_password_done')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password_done')
        try:
            uid = request.session.get('uid')
            if not uid:
                messages.error(request, 'Invalid session. Please try again.')
                return redirect('forgot_password')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(
                request, 'Your password has been reset successfully.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User not found. Please try again.')
            return redirect('forgot_password')
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('myAccount')

    return render(request, 'accounts/reset_password_done.html')
