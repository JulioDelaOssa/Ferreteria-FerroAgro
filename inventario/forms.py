from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Categoria, Cliente, Producto, Proveedor

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Descripción de la categoría',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'activo': 'Categoría activa'
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del proveedor'
            }),
            'contacto': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Persona de contacto'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dirección'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'contacto': 'Contacto',
            'telefono': 'Teléfono',
            'email': 'Correo',
            'direccion': 'Dirección',
            'activo': 'Proveedor activo'
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'documento', 'telefono', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre completo del cliente'
            }),
            'documento': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Número de documento o NIT'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Teléfono del cliente'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'correo@ejemplo.com'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'documento': 'Documento',
            'telefono': 'Teléfono',
            'correo': 'Correo'
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'stock_minimo',
            'imagen',
            'categoria',
            'proveedor',
            'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Descripción del producto',
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
                'placeholder': 'Cantidad inicial',
                'min': '0'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Stock mínimo',
                'min': '0'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-input'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-input'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'stock': 'Stock inicial',
            'stock_minimo': 'Stock mínimo',
            'imagen': 'Imagen del producto',
            'categoria': 'Categoría',
            'proveedor': 'Proveedor',
            'activo': 'Producto activo'
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')

        return precio


class AjusteStockForm(forms.Form):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste')
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label='Tipo de movimiento',
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    cantidad = forms.IntegerField(
        label='Cantidad',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Cantidad',
            'min': '1'
        })
    )

    motivo = forms.CharField(
        label='Causa',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Causa del ajuste',
            'rows': 3
        })
    )


class VentaForm(forms.Form):
    cantidad = forms.IntegerField(
        label='Cantidad a vender',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Cantidad',
            'min': '1'
        })
    )


class VentaCarritoForm(forms.Form):
    cliente_nombre = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre del cliente'
        })
    )

    cliente_documento = forms.CharField(
        label='Documento',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Documento o NIT'
        })
    )

    cliente_telefono = forms.CharField(
        label='Teléfono',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Teléfono del cliente'
        })
    )

    metodo_pago = forms.ChoiceField(
        label='Método de pago',
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia'),
            ('tarjeta', 'Tarjeta'),
            ('credito', 'Crédito')
        ],
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    descuento = forms.DecimalField(
        label='Descuento',
        required=False,
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0',
            'step': '0.01',
            'min': '0'
        })
    )

    observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Observaciones de la venta',
            'rows': 3
        })
    )


class VendedorForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nombre',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre del vendedor'
        })
    )

    last_name = forms.CharField(
        label='Apellido',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apellido del vendedor'
        })
    )

    email = forms.EmailField(
        label='Correo',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuario'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Usuario de acceso'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

class VendedorEditarForm(forms.ModelForm):
    password = None

    first_name = forms.CharField(
        label='Nombre',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre del vendedor'
        })
    )

    last_name = forms.CharField(
        label='Apellido',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apellido del vendedor'
        })
    )

    email = forms.EmailField(
        label='Correo',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    is_active = forms.BooleanField(
        label='Vendedor activo',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        labels = {
            'username': 'Usuario'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Usuario de acceso'
            })
        }
