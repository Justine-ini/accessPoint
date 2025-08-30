from datetime import time, datetime, date
from django.db import models
from accounts.utils import send_notification_email
from accounts.models import User, UserProfile
# Create your models here.


class Vendor(models.Model):

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

    def is_open(self):
        opening_hours = OpeningHour.objects.filter(
            vendor=self
        ).order_by('day', '-from_hour')

        # Get today's opening hours
        today = date.today().isoweekday()  # Monday=1, Sunday=7
        today_opening_hours = opening_hours.filter(day=today)

        now = datetime.now()
        current_time_obj = now.time()
        is_open = False  # default closed

        if today_opening_hours.exists():
            for hour in today_opening_hours:
                if not hour.is_closed:
                    start_time = datetime.strptime(
                        hour.from_hour, "%I:%M %p").time()
                    end_time = datetime.strptime(
                        hour.to_hour, "%I:%M %p").time()

                    # Only allow same-day hours
                    if start_time <= current_time_obj <= end_time:
                        is_open = True
                        break
                    # else:
                    #     is_open = False
        return is_open

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
                    'to_email': self.user.email,
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


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [
    (time(h, m).strftime('%I:%M %p'),
     time(h, m).strftime('%I:%M %p'))
    for h in range(0, 24)
    for m in (0, 30)
]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(
        max_length=10,
        choices=HOUR_OF_DAY_24,
        blank=True,
        help_text="Opening time (e.g. '09:00 AM')"
    )
    to_hour = models.CharField(
        max_length=10,
        choices=HOUR_OF_DAY_24,
        blank=True,
        help_text="Closing time (e.g. '05:30 PM')"
    )
    is_closed = models.BooleanField(
        default=False,
        help_text="Tick if the vendor is closed all day"
    )

    class Meta:
        ordering = ("day", "-from_hour")
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    def __str__(self):
        """
        Return a human-readable representation of the opening hours.
        Shows day name and time range or 'Closed'.
        """
        day_name = self.get_day_display(
        )  # Inbuilt helper function to display day name e.g Sunday
        if self.is_closed:
            return f"{day_name}: Closed"
        return f"{day_name}: {self.from_hour} - {self.to_hour}"
