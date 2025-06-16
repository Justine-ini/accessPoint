from django.core.exceptions import PermissionDenied


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
