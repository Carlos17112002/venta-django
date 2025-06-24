from django import forms
from .models import Producto
from django.contrib.auth.models import User
from .models import Producto, Talla, Color  


class ProductoForm(forms.ModelForm):
    tallas = forms.ModelMultipleChoiceField(
        queryset=Talla.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
    )
    colores = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
    )

    class Meta:
        model = Producto
        exclude = ['creador']
        # No uses 'fields = "__all__"' junto con exclude

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'categoria':
                self.fields[field].widget.attrs.update({'class': 'form-select'})
            elif field == 'imagen':
                self.fields[field].widget.attrs.update({'class': 'form-control', 'accept': 'image/*'})
            elif field not in ['tallas', 'colores']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        


class UsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


class CheckoutForm(forms.Form):
    OPCIONES_ENVIO = (
        ('retiro', 'Retiro en tienda'),
        ('domicilio', 'Envío a domicilio'),
    )

    metodo_envio = forms.ChoiceField(
        choices=OPCIONES_ENVIO,
        widget=forms.RadioSelect,
        label="Método de entrega"
    )
    direccion = forms.CharField(
        required=False,
        label="Dirección de entrega",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Ej: Calle Falsa 123, Santiago"})
    )
    telefono = forms.CharField(
        max_length=20,
        label="Número de contacto",
        widget=forms.TextInput(attrs={"placeholder": "Ej: +56912345678"})
    )

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get("metodo_envio")
        direccion = cleaned_data.get("direccion")

        if metodo == "domicilio" and not direccion:
            self.add_error('direccion', "Debe ingresar una dirección para el envío a domicilio.")
            
            
            
