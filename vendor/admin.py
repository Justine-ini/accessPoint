from django.contrib import admin
from .models import Vendor, OpeningHour


class VendorAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    list_display = ('get_vendor', 'vendor_license',
                    'is_approved', 'created_at')
    search_fields = ('vendor_name',)
    list_filter = ()
    fieldsets = ()
    list_editable = ('is_approved',)

    def get_vendor(self, obj):
        return obj.vendor_name

    get_vendor.short_description = "Vendor Name"


class OpeningHourAdmin(admin.ModelAdmin):
    list_display = (
        'vendor', 'day', 'from_hour', 'to_hour', 'is_closed'
    )


admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
