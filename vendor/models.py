from django.db import models
from accounts.models import User, UserProfile

# Create your models here.


class Vendor(models.Model):
    """
    Represents a vendor profile associated with a user and user profile.
    Fields:
        user (OneToOneField): The user account associated with the vendor.
        user_profile (OneToOneField): The user profile associated with the vendor.
        vendor_name (CharField): The name of the vendor.
        vendor_license (ImageField): The license image for the vendor.
        is_approved (BooleanField): Approval status of the vendor.
        created_at (DateTimeField): Timestamp when the vendor was created.
        modified_at (DateTimeField): Timestamp when the vendor was last modified.
    Methods:
        __str__(): Returns the vendor's name as its string representation.
    """
    user = models.OneToOneField(
        User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.vendor_name)
