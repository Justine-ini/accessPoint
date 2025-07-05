from django.db import models
from accounts.utils import send_notification_email
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
    slug = models.SlugField(max_length=100, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.vendor_name)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Get the existing record from DB
            original = Vendor.objects.get(pk=self.pk)

            # Check if approval status changed
            if original.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_vendor_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved is True:
                    # Send "approved" email
                    mail_subject = 'Congratulations! your restaurant is approved'
                    send_notification_email(
                        mail_subject, mail_template, context)
                else:
                    # Send "disapproved" or "revoked" email
                    mail_subject = 'Unfortunately, your restaurant is not approved'
                    send_notification_email(
                        mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)
