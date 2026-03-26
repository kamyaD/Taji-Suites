# forms.py
from django import forms
from .models import KitchenStockSheet, LNKStockSheet, Product
from .models import BarStockSheet

# For updating stock
class ProductStockForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['stock']

# For creating new product
class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'department', 'location', 'image']



# forms.py
class BarStockForm(forms.ModelForm):
    class Meta:
        model = BarStockSheet
        fields = ['item', 'category', 'opening_stock', 'sold', 'rate', 'unit_cost', 'add', 'date']

        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'opening_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'sold': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'add': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class LNKStockForm(forms.ModelForm):
    class Meta:
        model = LNKStockSheet
        fields = ['item', 'sold','opening_stock', 'rate', 'add', 'date']

        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'sold': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'unit_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'add': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class KitchenStockForm(forms.ModelForm):
    class Meta:
        model = KitchenStockSheet
        fields = ['item', 'opening_stock', 'sold', 'rate','add', 'date']

        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'sold': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'unit_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'add': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }