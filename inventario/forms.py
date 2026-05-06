from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'proveedor']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Descripcion del producto',
                'rows': 3
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-input'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-input'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripcion',
            'precio': 'Precio',
            'stock': 'Stock',
            'categoria': 'Categoria',
            'proveedor': 'Proveedor'
        }

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')

        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')

        return stock

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')

        return precio