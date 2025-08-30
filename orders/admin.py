from django.contrib import admin
from .models import Payment, Order, OrderedFood


# Register your models here.
class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    extra = 0
    readonly_fields = ('payment', 'user', 'fooditem',
                       'quantity', 'price', 'amount')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'name', 'total',
                    'payment_method', 'status', 'is_ordered', 'created_at')
    inlines = [OrderedFoodInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
