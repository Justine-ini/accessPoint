from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

# Register your models here.

class CustomUserAdmin(UserAdmin):
    filter_horizontal = ()
    ordering = ('-date_joined',)
    list_display = ('first_name', 'last_name', 'username', 'email', 'role', 'is_active', 'is_admin', 'is_superuser')
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    list_display = ('get_username', 'country', 'state', 'city', 'created_at')
    list_filter = ()
    fieldsets = ()

    def get_username(self, obj):
        return obj.user.username if obj.user else None
    
    get_username.short_description = "Username"

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
