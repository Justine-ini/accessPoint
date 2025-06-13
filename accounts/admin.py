from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

# Register your models here.

class CustomUserAdmin(UserAdmin):
    filter_horizontal = ()
    ordering = ('-date_joined',)
    list_display = ('first_name', 'last_name', 'email', 'role', 'is_active', 'is_admin', 'is_superuser')
    list_filter = ()
    fieldsets = ()

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
