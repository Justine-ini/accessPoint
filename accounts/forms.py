"""Forms for the accounts app."""
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django import forms
from .models import User


class UserForm(forms.ModelForm):
    """Form for creating and updating User instances."""

    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

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
            raise forms.ValidationError("First name must only contain letters.")
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