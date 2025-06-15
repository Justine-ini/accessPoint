from django.contrib import admin
from .models import Vendor


class VendorProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    list_display = ('get_vendor', 'vendor_license',
                    'is_approved', 'created_at')
    list_filter = ()
    fieldsets = ()

    def get_vendor(self, obj):
        return obj.vendor_name

    get_vendor.short_description = "Vendor Name"


admin.site.register(Vendor, VendorProfileAdmin)
