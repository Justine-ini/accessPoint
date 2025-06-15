from django import forms
from .models import Vendor


class VendorForm(forms.ModelForm):
    """Form for creating and updating Vendor instances."""
    class Meta:
        """Meta options for VendorForm."""
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
