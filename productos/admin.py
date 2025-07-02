from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito
from .models import Producto, Talla, Color
from django import forms
from .models import Pedido, ItemPedido
from .models import ImagenProducto




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
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'creador')
    list_filter = ('categoria', 'creador')
    search_fields = ('nombre', 'marca')
    filter_horizontal = ('tallas', 'colores')
    readonly_fields = ('creador',)  # Para que el creador se vea pero no se pueda editar

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Solo muestra productos creados por el usuario logueado
        return qs.filter(creador=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            # Asigna el usuario logueado como creador al crear un producto
            obj.creador = request.user
        obj.save()
    
    
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



class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

