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
        
        
from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, label="Nombre")
    last_name = forms.CharField(max_length=100, label="Apellido")
    email = forms.EmailField(label="Correo electrónico")
    rut = forms.CharField(max_length=12, label="RUT")
    direccion = forms.CharField(max_length=255, label="Dirección")
    telefono = forms.CharField(max_length=20, label="Teléfono")

    class Meta:
        model = Profile
        fields = ['rut', 'direccion', 'telefono']


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
            
            
class RegistroForm(UserCreationForm):
    nombres = forms.CharField(max_length=100, required=True, label="Nombres")
    apellidos = forms.CharField(max_length=100, required=True, label="Apellidos")
    email = forms.EmailField(required=True)
    rut = forms.CharField(max_length=12, required=True)
    direccion = forms.CharField(max_length=255, required=True)
    telefono = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'nombres', 'apellidos', 'email', 'rut', 'direccion', 'telefono']
