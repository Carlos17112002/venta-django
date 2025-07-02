from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from decimal import Decimal
from django.utils import timezone


class Talla(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Color(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    CATEGORIAS = [
        ('Hombre', 'Hombre'),
        ('Mujer', 'Mujer'),
        ('Accesorio', 'Accesorio'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    marca = models.CharField(max_length=50, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos')
    tallas = models.ManyToManyField(Talla)
    colores = models.ManyToManyField(Color)
    pagado = models.BooleanField(default=False)
    
    def calcular_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return self.nombre


# models.py
class Carrito(models.Model):
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return f"Carrito de {self.usuario or 'anónimo'}"


# models.py
class ItemCarrito(models.Model):
    carrito = models.ForeignKey('Carrito', related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    talla = models.ForeignKey('Talla', on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def imagen_color(self):
        # Buscar la primera imagen del producto con el color seleccionado
        imagen = self.producto.imagenes.filter(color=self.color).first()
        if imagen:
            return imagen.imagen.url
        # Si no hay imagen con ese color, devolver la imagen principal
        return self.producto.imagen.url if hasattr(self.producto, 'imagen') and self.producto.imagen else ''


class Favorito(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favoritos')
    producto = models.ForeignKey(
        'Producto', on_delete=models.CASCADE, related_name='favoritos')
    imagen_principal = models.ImageField(
        upload_to='favoritos/', blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')

    def save(self, *args, **kwargs):
        # Si no tiene imagen principal, la asignamos al guardar
        if not self.imagen_principal:
            primera_imagen = self.producto.imagenes.first()
            if primera_imagen:
                self.imagen_principal = primera_imagen.imagen
        super().save(*args, **kwargs)



class Pedido(models.Model):
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    tipo_entrega = models.CharField(max_length=20, choices=[('retiro', 'Retiro en tienda'), ('envio', 'Envío a domicilio')])
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20)
    fecha = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)
    creado = models.DateTimeField(default=timezone.now)
    
# Para marcar si ya se pagó el pedido

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario or "Anónimo"}'

    def calcular_total(self):
        return sum(item.subtotal() for item in self.items.all())
    
    
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    talla = models.ForeignKey(Talla, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'    
class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    

    def save(self, *args, **kwargs):
        if not self.total or self.total == 0:
            self.total = self.producto.precio * Decimal(self.cantidad)
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rut = models.CharField(max_length=12, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Imagen de {self.producto.nombre} - Color: {self.color.nombre if self.color else 'Sin color'}"




