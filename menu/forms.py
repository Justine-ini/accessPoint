from django import forms
from .models import Category, FoodItem
from accounts.validators import allow_only_images_validator


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_name', 'description')

    def clean_category_name(self):
        name = self.cleaned_data.get('category_name')
        if name:
            return name[0].upper() + name[1:]
        return name


class FoodItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",           # ← this becomes the first choice
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    image = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images_validator]
    )

    class Meta:
        model = FoodItem
        fields = (
            'category',
            'food_title',
            'description',
            'price',
            'image',
            'is_available',
        )
