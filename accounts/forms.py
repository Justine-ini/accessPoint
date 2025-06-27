"""Forms for the accounts app."""
from django.core.validators import validate_email
from django import forms
from .models import User, UserProfile
from .validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    """Form for creating and updating User instances."""

    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), required=True)

    class Meta:
        """Meta options for UserForm."""
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get('first_name').strip().title()
        last_name = cleaned_data.get('last_name').strip().title()
        email = cleaned_data.get('email').strip()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Name validation
        if first_name and not first_name.isalpha():
            raise forms.ValidationError(
                "First name must only contain letters.")
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last name must only contain letters.")

        # Password validation
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Email validation
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError("Invalid email format.")

        return cleaned_data


class LoginForm(forms.Form):
    """Form for user login."""
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }), required=True
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }), required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email').strip().lower()
        password = cleaned_data.get('password')

        if not email or not password:
            raise forms.ValidationError("Email and password are required.")

        return cleaned_data


class UserProfileForm(forms.ModelForm):

    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Start typing...'
        })
    )
    profile_picture = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator]
    )
    cover_photo = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator]
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'cover_photo',
            'address',
            'country',
            'state',
            'city',
            'pincode',
            'latitude',
            'longitude',
        ]
        widgets = {
            'latitude': forms.TextInput(attrs={'readonly': 'readonly'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
