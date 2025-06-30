from django import forms
from .models import Category, FoodItem


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
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
