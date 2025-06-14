"""Views for user registration and management."""
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm
from .models import User

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