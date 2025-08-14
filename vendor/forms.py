from django import forms
from accounts.validators import allow_only_images_validator
from .models import Vendor, OpeningHour


class VendorForm(forms.ModelForm):
    """Form for creating and updating Vendor instances."""
    vendor_license = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator]
    )

    class Meta:
        """Meta options for VendorForm."""
        model = Vendor
        fields = ['vendor_name', 'vendor_license']


class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
