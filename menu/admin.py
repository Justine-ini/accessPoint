from django.contrib import admin
from .models import FoodItem, Category

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ['vendor', 'category_name', 'created_at', 'updated_at']
    # Accessing the 'vendor_name' field from the related 'vendor' model (vendor__vendor_name)
    search_fields = ('category_name', 'vendor__vendor_name')


class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ['vendor', 'food_title', 'category',
                    'price', 'is_available', 'created_at', 'updated_at']
    list_filter = ('is_available',)
    # Accessing the 'vendor_name' field from the related 'vendor' model (vendor__vendor_name)
    search_fields = ('category__category_name',
                     'vendor__vendor_name', 'food_title')


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
