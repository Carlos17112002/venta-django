from django.shortcuts import redirect
from .models import Favorito
from django.http import JsonResponse
from .models import Producto, Favorito
from django.shortcuts import get_object_or_404, redirect
from .forms import UsernameForm
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Carrito, ItemCarrito
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import os
from django.conf import settings
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Producto
from .forms import ProductoForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count
from django.conf import settings
import os
from .models import Producto
from .forms import ProductoForm
from django.shortcuts import get_object_or_404, redirect
from .models import ItemCarrito, Carrito

from django.shortcuts import render, redirect
from .forms import CheckoutForm
from .models import Pedido
from .models import Producto, Talla, Color


from django.db.models import Q
import os
from django.conf import settings

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .models import Venta

def lista_productos(request):
    filtros = {
        'q': request.GET.get('q', ''),
        'categoria': request.GET.get('categoria', ''),
        'marca': request.GET.get('marca', ''),
        'precio_min': request.GET.get('precio_min', ''),
        'precio_max': request.GET.get('precio_max', ''),
    }

    productos = Producto.objects.all()

    if filtros['q']:
        productos = productos.filter(nombre__icontains=filtros['q'])
    if filtros['categoria']:
        productos = productos.filter(categoria=filtros['categoria'])
    if filtros['marca']:
        productos = productos.filter(marca=filtros['marca'])
    if filtros['precio_min']:
        try:
            productos = productos.filter(precio__gte=float(filtros['precio_min']))
        except ValueError:
            pass
    if filtros['precio_max']:
        try:
            productos = productos.filter(precio__lte=float(filtros['precio_max']))
        except ValueError:
            pass

    # Aquí el procesamiento de tallas y colores:
    for producto in productos:
        producto.lista_tallas = producto.tallas.all()
        producto.lista_colores = producto.colores.all()

    marcas = Producto.objects.values_list('marca', flat=True)\
        .distinct().exclude(marca__isnull=True).exclude(marca__exact='').order_by('marca')

    if request.user.is_authenticated:
        favoritos_ids = list(request.user.favoritos.values_list('producto_id', flat=True))
    else:
        favoritos_ids = []

    context = {
        'productos': productos,
        'favoritos_ids': favoritos_ids,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/productos_list.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'index.html', {
        'productos': productos,
        'categorias': Producto.CATEGORIAS,
        'marcas': marcas,
        'filtros': filtros,
        'favoritos_ids': favoritos_ids,
        'MEDIA_URL': settings.MEDIA_URL,
    })



# views.py

def ver_carrito(request):
    if request.user.is_authenticated:
        # Intentamos recuperar el carrito del usuario
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        # Si no hay sesión activa, la creamos
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Obtenemos el carrito asociado a la sesión
        carrito, created = Carrito.objects.get_or_create(session_key=session_key, usuario=None)

    items = ItemCarrito.objects.filter(carrito=carrito)
    total = sum(item.producto.precio * item.cantidad for item in items)

    return render(request, 'carrito.html', {'items': items, 'total': total})


def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})


def mujer(request):
    return render(request, 'mujer.html')


def index(request):
    return render(request, 'index.html')


def hombre(request):
    return render(request, 'hombre.html')

def base(request):
    return render(request, 'base.html')


def carrusel(request):
    media_path = os.path.join(settings.MEDIA_ROOT, 'productos')
    imagenes = []
    if os.path.exists(media_path):
        for nombre in os.listdir(media_path):
            if nombre.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                imagenes.append('productos/' + nombre)
    return render(request, 'carrusel.html', {'imagenes': imagenes})


def productos_hombre(request):
    # Parámetros GET
    q = request.GET.get('q', '')
    marca = request.GET.get('marca')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    # Base: solo productos de categoría 'Hombre'
    productos = Producto.objects.filter(categoria="Hombre")

    # Filtros dinámicos
    if q:
        productos = productos.filter(nombre__icontains=q)
    if marca:
        productos = productos.filter(marca=marca)
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Carrusel de imágenes desde /media/productos/
    media_path = os.path.join(settings.MEDIA_ROOT, 'productos')
    imagenes_carrusel = []
    if os.path.exists(media_path):
        for nombre in os.listdir(media_path):
            if nombre.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                imagenes_carrusel.append('productos/' + nombre)

    # Favoritos del usuario autenticado
    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(
            request.user.favoritos.values_list('producto_id', flat=True))

    # Obtener marcas disponibles en esta categoría (para el filtro select)
    marcas = Producto.objects.filter(categoria="Hombre")\
                .values_list('marca', flat=True)\
                .distinct()

    return render(request, 'hombre.html', {
        'productos': productos,
        'imagenes_carrusel': imagenes_carrusel,
        'MEDIA_URL': settings.MEDIA_URL,
        'favoritos_ids': favoritos_ids,
        'marcas': marcas,
        'filtros': {
            'q': q,
            'marca': marca,
            'precio_min': precio_min,
            'precio_max': precio_max,
        }
    })


def productos_mujer(request):
    # Parámetros GET para filtro
    q = request.GET.get('q', '')
    marca = request.GET.get('marca')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    # Filtrar solo categoría Mujer
    productos = Producto.objects.filter(categoria__iexact="Mujer")

    # Aplicar filtros dinámicos
    if q:
        productos = productos.filter(nombre__icontains=q)
    if marca:
        productos = productos.filter(marca=marca)
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Imágenes para carrusel
    media_path = os.path.join(settings.MEDIA_ROOT, 'productos')
    imagenes_carrusel = []
    if os.path.exists(media_path):
        for nombre in os.listdir(media_path):
            if nombre.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                imagenes_carrusel.append('productos/' + nombre)

    # Favoritos usuario
    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(
            request.user.favoritos.values_list('producto_id', flat=True))

    # Marcas disponibles en Mujer para filtro select
    marcas = Producto.objects.filter(categoria__iexact="Mujer")\
                .values_list('marca', flat=True).distinct()

    return render(request, 'mujer.html', {
        'productos': productos,
        'imagenes_carrusel': imagenes_carrusel,
        'MEDIA_URL': settings.MEDIA_URL,
        'favoritos_ids': favoritos_ids,
        'marcas': marcas,
        'filtros': {
            'q': q,
            'marca': marca,
            'precio_min': precio_min,
            'precio_max': precio_max,
        }
    })


from django.shortcuts import get_object_or_404, redirect
from .models import Producto, Carrito, ItemCarrito

def agregar_al_carrito(request, producto_id):
    if request.method == "POST":
        producto = Producto.objects.get(id=producto_id)
        talla_id = request.POST.get('talla')
        color_id = request.POST.get('color')
        cantidad = int(request.POST.get('cantidad', 1))

        # 🔽 Convertimos los IDs a instancias
        talla = Talla.objects.get(id=talla_id)
        color = Color.objects.get(id=color_id)

        if request.user.is_authenticated:
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            carrito, created = Carrito.objects.get_or_create(session_key=session_key, usuario=None)

      
        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            talla=talla,
            color=color,
            cantidad=cantidad
        )

        return redirect('ver_carrito')  # o la URL que corresponda


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, creador=request.user)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.save()  # Guardar antes de asignar ManyToMany
            
            # Obtener listas de IDs de tallas y colores del formulario
            tallas_ids = request.POST.getlist('tallas')  # plural, que es el nombre del campo
            colores_ids = request.POST.getlist('colores') 
            
            # Asignar relaciones ManyToMany correctamente
            producto.tallas.set(tallas_ids)
            producto.colores.set(colores_ids)
            
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'form': form, 'producto': producto})


@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, creador=request.user)
    if request.method == 'POST':
        producto.delete()
        return redirect('admin_custom')
    return render(request, 'eliminar_producto.html', {'producto': producto})


def login_personalizado(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Esto guarda la sesión para cualquier usuario
            login(request, user)
            if user.is_superuser:
                return redirect('admin_custom')
            else:
                return redirect('panel_usuario')
        else:
            error = "Usuario o contraseña incorrectos"
            return render(request, 'login.html', {'error': error})
    return render(request, 'login.html')


@login_required
def panel_usuario(request):
    query = request.GET.get('q')
    if query:
        productos = Producto.objects.filter(nombre__icontains=query)
    else:
        productos = Producto.objects.all()

    # Obtener imágenes del carrusel
    import os
    from django.conf import settings
    media_path = os.path.join(settings.MEDIA_ROOT, 'productos')
    imagenes_carrusel = []
    if os.path.exists(media_path):
        for nombre in os.listdir(media_path):
            if nombre.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                imagenes_carrusel.append('productos/' + nombre)

    return render(request, 'index.html', {
        'productos': productos,
        'imagenes_carrusel': imagenes_carrusel,
        'MEDIA_URL': settings.MEDIA_URL,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_custom(request):
    productos = Producto.objects.all()
    return render(request, 'admin.html', {'productos': productos})


@login_required
def perfil_usuario(request):
    user = request.user
    username_form = UsernameForm(instance=user)
    password_form = PasswordChangeForm(user)
    username_success = False
    password_success = False

    if request.method == 'POST':
        if 'cambiar_usuario' in request.POST:
            username_form = UsernameForm(request.POST, instance=user)
            if username_form.is_valid():
                username_form.save()
                username_success = True
        elif 'cambiar_contrasena' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                password_success = True

    return render(request, 'perfil_usuario.html', {
        'username_form': username_form,
        'password_form': password_form,
        'username_success': username_success,
        'password_success': password_success,
    })


def marcas(request):
    q = request.GET.get('q', '').strip()
    marca = request.GET.get('marca', '')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    categoria = request.GET.get('categoria', '')

    productos = Producto.objects.all()

    if categoria:
        productos = productos.filter(categoria__iexact=categoria)

    if q:
        productos = productos.filter(nombre__icontains=q)

    if marca:
        productos = productos.filter(marca__iexact=marca)

    if precio_min:
        try:
            productos = productos.filter(precio__gte=float(precio_min))
        except ValueError:
            pass

    if precio_max:
        try:
            productos = productos.filter(precio__lte=float(precio_max))
        except ValueError:
            pass

    # Obtener marcas para el filtro lateral
    marcas = Producto.objects.values('marca')\
        .annotate(total=Count('id'))\
        .order_by('marca')

    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(request.user.favoritos.values_list('producto_id', flat=True))

    filtros = {
        'q': q,
        'marca': marca,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'categoria': categoria,
    }

    return render(request, 'marcas.html', {
        'productos': productos,
        'marcas': marcas,
        'filtros': filtros,
        'favoritos_ids': favoritos_ids,
    })


def productos_accesorio(request):
    filtros = {
        'q': request.GET.get('q', '').strip(),
        'marca': request.GET.get('marca', '').strip(),
        'precio_min': request.GET.get('precio_min', '').strip(),
        'precio_max': request.GET.get('precio_max', '').strip(),
    }

    productos = Producto.objects.filter(categoria__iexact="accesorio")

    if filtros['q']:
        productos = productos.filter(nombre__icontains=filtros['q'])
    if filtros['marca']:
        productos = productos.filter(marca=filtros['marca'])
    if filtros['precio_min']:
        try:
            productos = productos.filter(precio__gte=float(filtros['precio_min']))
        except ValueError:
            pass
    if filtros['precio_max']:
        try:
            productos = productos.filter(precio__lte=float(filtros['precio_max']))
        except ValueError:
            pass

    media_path = os.path.join(settings.MEDIA_ROOT, 'productos')
    imagenes_carrusel = []
    if os.path.exists(media_path):
        for nombre in os.listdir(media_path):
            if nombre.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                imagenes_carrusel.append('productos/' + nombre)

    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(
            request.user.favoritos.values_list('producto_id', flat=True))

    marcas = Producto.objects.filter(categoria__iexact="accesorio")\
                .values_list('marca', flat=True).distinct()

    context = {
        'productos': productos,
        'imagenes_carrusel': imagenes_carrusel,
        'MEDIA_URL': settings.MEDIA_URL,
        'favoritos_ids': favoritos_ids,
        'filtros': filtros,
        'marcas': marcas,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Renderizar solo el fragmento con los productos para AJAX
        html = render_to_string('partials/productos_list.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'accesorios.html', context)


@login_required
def toggle_favorito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    favorito, creado = Favorito.objects.get_or_create(
        usuario=request.user, producto=producto)
    if not creado:
        favorito.delete()
        es_favorito = False
    else:
        es_favorito = True
    return JsonResponse({'es_favorito': es_favorito})


# views.py


@login_required
def mis_favoritos(request):
    favoritos = Favorito.objects.filter(
        usuario=request.user).select_related('producto')
    return render(request, 'mis_favoritos.html', {'favoritos': favoritos})


def eliminar_item_carrito(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__session_key=session_key, carrito__usuario=None)
    item.delete()
    return redirect('ver_carrito')


def actualizar_cantidad_carrito(request, item_id):
    # Asegurarse de que haya una sesión activa
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # Obtener el carrito según el tipo de usuario
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user).first()
    else:
        carrito = Carrito.objects.filter(session_key=session_key, usuario=None).first()

    # Si no hay carrito, no se puede actualizar nada
    if not carrito:
        return redirect('ver_carrito')

    # Obtener el item del carrito
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)

    # Actualizar o eliminar el item
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad > 0:
            item.cantidad = cantidad
            item.save()
        else:
            item.delete()

    return redirect('ver_carrito')


TALLAS = Talla.objects.all()
COLORES = Color.objects.all()


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Talla, Color
from .forms import ProductoForm

from .models import Producto, Talla, Color

def agregar_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.creador = request.user
            producto.save()
            form.save_m2m()  # <- Importante para guardar tallas y colores
            return redirect('lista_productos')
    else:
        form = ProductoForm()

    return render(request, 'agregar_producto.html', {'form': form})






def checkout_view(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Aquí puedes guardar la info del pedido o llevarlo al paso siguiente
            # Por ahora redirigiremos a una página de confirmación de pago simulada
            request.session['checkout_data'] = form.cleaned_data
            return redirect('pago')  # vista siguiente (paso final)
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {'form': form})


def pago_view(request):
    # Por ejemplo, obtener el último pedido del usuario (o usa otro criterio)
    if request.user.is_authenticated:
        pedido = Pedido.objects.filter(usuario=request.user).order_by('-id').first()
    else:
        pedido = None  # O manejar pedido para usuario anónimo

    if not pedido:
        # No hay pedido, redirige a carrito o checkout
        return redirect('checkout')

    context = {
        'pedido': pedido
    }
    return render(request, 'pago.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages

def procesar_checkout(request):
    if request.method == 'POST':
        tipo_entrega = request.POST.get('tipo_entrega')
        direccion = request.POST.get('direccion', '')
        telefono = request.POST.get('telefono')

        if not tipo_entrega or not telefono:
            # Aquí podrías mostrar un error o redirigir con mensaje
            return redirect('checkout')

        pedido = Pedido.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            tipo_entrega=tipo_entrega,
            direccion=direccion if tipo_entrega == 'envio' else '',
            telefono=telefono,
        )

        # Aquí normalmente irías a la página de pago o confirmación
        return redirect('pago')  # Cambia 'pago' por la url de tu proceso de pago

    return redirect('checkout')  # Si no es POST, regresa a checkout

from django.shortcuts import redirect

def procesar_pago(request):
    if request.method == 'POST':
        # Aquí procesas el pago (lógica, integración, etc.)
        # Por ahora simplemente redirigimos a una página de "gracias"
        return redirect('gracias')
    else:
        # Si acceden con GET, redirige o muestra error
        return redirect('pago')


def gracias_view(request):
    return render(request, 'gracias.html')

def home_view(request):
    # Aquí devuelves el template principal o lo que quieras para la página inicial
    return render(request, 'index.html')


def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    tallas = producto.tallas.all()
    colores = producto.colores.all()

    return render(request, "productos/producto_detalle.html", {
        "producto": producto,
        "tallas": tallas,
        "colores": colores,
    })

def lista_productos_hombre(request):
    categoria = 'hombre'
    filtros = {
        'q': request.GET.get('q', ''),
        'marca': request.GET.get('marca', ''),
        'precio_min': request.GET.get('precio_min', ''),
        'precio_max': request.GET.get('precio_max', ''),
    }

    productos = Producto.objects.filter(categoria=categoria)

    if filtros['q']:
        productos = productos.filter(nombre__icontains=filtros['q'])
    if filtros['marca']:
        productos = productos.filter(marca=filtros['marca'])
    if filtros['precio_min']:
        try:
            productos = productos.filter(precio__gte=float(filtros['precio_min']))
        except ValueError:
            pass
    if filtros['precio_max']:
        try:
            productos = productos.filter(precio__lte=float(filtros['precio_max']))
        except ValueError:
            pass

    marcas = Producto.objects.filter(categoria=categoria)\
        .values_list('marca', flat=True)\
        .distinct()\
        .exclude(marca__isnull=True)\
        .exclude(marca__exact='')\
        .order_by('marca')

    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(request.user.favoritos.values_list('producto_id', flat=True))

    context = {
        'productos': productos,
        'favoritos_ids': favoritos_ids,
        'marcas': marcas,
        'filtros': filtros,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/productos_list.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'hombre.html', context)


def lista_productos_mujer(request):
    categoria = 'mujer'
    filtros = {
        'q': request.GET.get('q', ''),
        'marca': request.GET.get('marca', ''),
        'precio_min': request.GET.get('precio_min', ''),
        'precio_max': request.GET.get('precio_max', ''),
    }

    productos = Producto.objects.filter(categoria=categoria)

    if filtros['q']:
        productos = productos.filter(nombre__icontains=filtros['q'])
    if filtros['marca']:
        productos = productos.filter(marca=filtros['marca'])
    if filtros['precio_min']:
        try:
            productos = productos.filter(precio__gte=float(filtros['precio_min']))
        except ValueError:
            pass
    if filtros['precio_max']:
        try:
            productos = productos.filter(precio__lte=float(filtros['precio_max']))
        except ValueError:
            pass

    marcas = Producto.objects.filter(categoria=categoria)\
        .values_list('marca', flat=True)\
        .distinct()\
        .exclude(marca__isnull=True)\
        .exclude(marca__exact='')\
        .order_by('marca')

    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(request.user.favoritos.values_list('producto_id', flat=True))

    context = {
        'productos': productos,
        'favoritos_ids': favoritos_ids,
        'marcas': marcas,
        'filtros': filtros,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/productos_list.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'mujer.html', context)


from django.db.models import Sum
from .models import Venta

@login_required
def historial_ventas(request):
    ventas = Venta.objects.filter(producto__creador=request.user).order_by('-fecha')

    # Filtros por fecha
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if desde:
        ventas = ventas.filter(fecha__date__gte=parse_date(desde))
    if hasta:
        ventas = ventas.filter(fecha__date__lte=parse_date(hasta))

    return render(request, 'venta/historial.html', {
        'ventas': ventas,
        'desde': desde,
        'hasta': hasta,
    })


import openpyxl
from django.http import HttpResponse
from .models import Venta

def exportar_excel(request):
    ventas = Venta.objects.filter(producto__creador=request.user).order_by('-fecha')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Ventas"

    # Cabeceras
    ws.append(['Producto', 'Cantidad', 'Precio unitario', 'Total', 'Fecha'])

    for venta in ventas:
        total = venta.cantidad * venta.precio_unitario
        ws.append([
            venta.producto.nombre,
            venta.cantidad,
            venta.precio_unitario,
            total,
            venta.fecha.strftime("%Y-%m-%d"),
        ])

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="historial_ventas.xlsx"'
    wb.save(response)
    return response
