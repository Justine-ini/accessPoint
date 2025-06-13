from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Update existing profile if it exists, create if missing
        try:
            # instance.userprofile.save() # Get related name
            updated_profile = UserProfile.objects.get(user=instance)
            updated_profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)

post_save.connect(post_save_create_profile_receiver, sender=User)