from django import forms
from .models import Vendor
from accounts.validators import allow_only_images_validator


class VendorForm(forms.ModelForm):
    """Form for creating and updating Vendor instances."""
    vendor_license = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator]
    )

    class Meta:
        """Meta options for VendorForm."""
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
