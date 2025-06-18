from django.core.exceptions import PermissionDenied
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def get_user_role(user):
    if user.role == 1:
        redirect_url = 'vendor-dashboard'
        return redirect_url
    elif user.role == 2:
        redirect_url = 'customer-dashboard'
        return redirect_url
    elif user.role is None and user.is_superuser:
        redirect_url = '/admin'
        return redirect_url
    else:
        redirect_url = 'home'
        return redirect_url


# Restrict vendor from accessing customer page
def vendor_restrict(user):
    """Restrict access to vendor dashboard for customers."""
    if user.role == 1:
        return True
    else:
        raise PermissionDenied(
            "You do not have permission to access this page.")


# Restrict customer from accessing vendor page
def customer_restrict(user):
    """Restrict access to customer dashboard for vendors."""
    if user.role == 2:
        return True
    else:
        raise PermissionDenied(
            "You do not have permission to access this page.")


def send_verification_email(request, user):

    current_site = get_current_site(request)

    mail_subject = 'Verify your email address'
    message = render_to_string(
        'accounts/emails/account_verification_email.html',
        {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        }
    )
    to_email = user.email
    mail = EmailMessage(
        subject=mail_subject, body=message, to=[to_email]
    )
    mail.send()
