from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito
from .models import Producto, Talla, Color
from django import forms
from .models import Pedido, ItemPedido



admin.site.register(Carrito)
admin.site.register(ItemCarrito)


@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'marca')
    filter_horizontal = ('tallas', 'colores')
    
    
class ProductoForm(forms.ModelForm):
    tallas = forms.ModelMultipleChoiceField(
        queryset=Talla.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # O usa SelectMultiple si prefieres dropdown
        required=False
    )
    colores = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'categoria', 'marca', 'stock', 'tallas', 'colores']    
    
    



class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'tipo_entrega', 'telefono', 'pagado', 'creado']
    list_filter = ['pagado', 'tipo_entrega']
    search_fields = ['usuario__username', 'telefono']
    inlines = [ItemPedidoInline]
