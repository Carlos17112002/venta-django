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
from .models import Pedido, ItemPedido
from .models import Producto, Talla, Color


from django.db.models import Q
import os
from django.conf import settings

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .models import Venta
from .forms import UserProfileForm


def lista_productos(request):
    filtros = {
        'q': request.GET.get('q', '').strip(),
        'categoria': request.GET.get('categoria', '').strip(),
        'marca': request.GET.get('marca', '').strip(),
        'precio_min': request.GET.get('precio_min', '').strip(),
        'precio_max': request.GET.get('precio_max', '').strip(),
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

    for producto in productos:
        producto.lista_tallas = producto.tallas.all()
        producto.lista_colores = producto.colores.all()
        producto.precio_formateado = f"{int(producto.precio):,}".replace(",", ".")

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

from django.shortcuts import render
from .models import Carrito

def ver_carrito(request):
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        carrito = Carrito.objects.filter(session_key=session_key, usuario=None).first()

    if carrito:
        items = carrito.items.select_related('producto', 'talla', 'color').all()
        total = sum(item.producto.precio * item.cantidad for item in items)
    else:
        items = []
        total = 0

    context = {
        'carrito': carrito,
        'items': items,
        'total': total,
    }
    return render(request, 'carrito.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm
from .models import Profile 

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['nombres']
            user.last_name = form.cleaned_data['apellidos']
            user.email = form.cleaned_data['email']
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.rut = form.cleaned_data['rut']
            profile.direccion = form.cleaned_data['direccion']
            profile.telefono = form.cleaned_data['telefono']
            profile.save()

            return redirect('login')
    else:
        form = RegistroForm()
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
    import os
    from django.conf import settings
    
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

    # Formatear precio para cada producto
    for producto in productos:
        producto.precio_formateado = f"{int(producto.precio):,}".replace(",", ".")

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
            request.user.favoritos.values_list('producto_id', flat=True)
        )

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
    import os
    from django.conf import settings

    # Parámetros GET para filtro
    q = request.GET.get('q', '')
    marca = request.GET.get('marca')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    # Filtrar solo categoría Mujer
    productos = Producto.objects.filter(categoria__iexact="Mujer").prefetch_related('imagenes')

    # Aplicar filtros dinámicos
    if q:
        productos = productos.filter(nombre__icontains=q)
    if marca:
        productos = productos.filter(marca=marca)
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Formatear precio para cada producto
    for producto in productos:
        producto.precio_formateado = f"{int(producto.precio):,}".replace(",", ".")

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
            request.user.favoritos.values_list('producto_id', flat=True)
        )

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

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

def agregar_al_carrito(request, producto_id):
    if request.method == "POST":
        producto = get_object_or_404(Producto, id=producto_id)
        talla_id = request.POST.get('talla')
        color_id = request.POST.get('color')
        cantidad = int(request.POST.get('cantidad', 1))

        talla = get_object_or_404(Talla, id=talla_id) if talla_id else None
        color = get_object_or_404(Color, id=color_id) if color_id else None

        if request.user.is_authenticated:
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            carrito, created = Carrito.objects.get_or_create(session_key=session_key, usuario=None)

        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            talla=talla,
            color=color,
            defaults={'cantidad': cantidad}
        )
        if not created:
            item.cantidad += cantidad
            item.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'nombre_producto': producto.nombre})
        else:
            return redirect('producto_detalle', producto_id=producto.id)




from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import Producto, ImagenProducto
from .forms import ProductoForm, ImagenProductoForm

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, creador=request.user)

    ImagenProductoFormSet = modelformset_factory(ImagenProducto, form=ImagenProductoForm, extra=1, can_delete=True)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        formset = ImagenProductoFormSet(request.POST, request.FILES, queryset=ImagenProducto.objects.filter(producto=producto))

        if form.is_valid() and formset.is_valid():
            producto = form.save(commit=False)
            producto.save()

            # Actualizar ManyToMany
            tallas_ids = request.POST.getlist('tallas')
            colores_ids = request.POST.getlist('colores')
            producto.tallas.set(tallas_ids)
            producto.colores.set(colores_ids)

            # Guardar imágenes (formset)
            images = formset.save(commit=False)
            # Asociar producto a cada imagen
            for img in images:
                img.producto = producto
                img.save()

            # Eliminar imágenes marcadas para borrar
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
        formset = ImagenProductoFormSet(queryset=ImagenProducto.objects.filter(producto=producto))

    return render(request, 'editar_producto.html', {
        'form': form,
        'formset': formset,
        'producto': producto,
    })



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

        # Verificamos si el usuario existe
        if not User.objects.filter(username=username).exists():
            # Usuario no existe, redirigir a registro
            return redirect('registro')

        user = authenticate(request, username=username, password=password)
        if user is not None:
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
    profile = user.profile

    username_form = UsernameForm(instance=user)
    profile_form = UserProfileForm(instance=profile, initial={
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    })
    password_form = PasswordChangeForm(user)

    username_success = password_success = profile_success = False

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

        elif 'actualizar_perfil' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                # Actualiza también campos del modelo User
                user.first_name = profile_form.cleaned_data['first_name']
                user.last_name = profile_form.cleaned_data['last_name']
                user.email = profile_form.cleaned_data['email']
                user.save()
                profile_form.save()
                profile_success = True

    return render(request, 'perfil_usuario.html', {
        'username_form': username_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'username_success': username_success,
        'password_success': password_success,
        'profile_success': profile_success,
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

    # Formatear precios
    for producto in productos:
        producto.precio_formateado = f"{int(producto.precio):,}".replace(",", ".")

    # Solo marcas únicas
    marcas = Producto.objects.values_list('marca', flat=True).distinct().order_by('marca')

    # Favoritos del usuario
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

    # Formatear precios
    for producto in productos:
        producto.precio_formateado = f"{int(producto.precio):,}".replace(",", ".")

    media_path = os.path.join(settings.MEDIA_ROOT, 'productos')
    imagenes_carrusel = []
    if os.path.exists(media_path):
        for nombre in os.listdir(media_path):
            if nombre.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                imagenes_carrusel.append('productos/' + nombre)

    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(request.user.favoritos.values_list('producto_id', flat=True))

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
        usuario=request.user,
        producto=producto
    )

    if not creado:
        favorito.delete()
        es_favorito = False
    else:
        # Asignar imagen principal al crear el favorito
        primera_imagen = producto.imagenes.first()
        if primera_imagen:
            favorito.imagen_principal = primera_imagen.imagen
            favorito.save()
        es_favorito = True

    return JsonResponse({'es_favorito': es_favorito})


# views.py


@login_required
def mis_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto').prefetch_related('producto__imagenes')

    # Crear una lista de IDs de productos favoritos para el template (más eficiente que hacer consultas en el template)
    favoritos_ids = favoritos.values_list('producto_id', flat=True)

    context = {
        'favoritos': favoritos,
        'favoritos_ids': list(favoritos_ids),
    }
    return render(request, 'mis_favoritos.html', context)



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


from django.shortcuts import get_object_or_404, redirect

def actualizar_cantidad_carrito(request, item_id):
    # Asegurarse de que haya una sesión activa para usuarios no autenticados
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

    # Intentar obtener el item que pertenece al carrito actual
    try:
        item = ItemCarrito.objects.get(id=item_id, carrito=carrito)
    except ItemCarrito.DoesNotExist:
        # El item no existe o no pertenece a este carrito
        return redirect('ver_carrito')

    # Solo procesar si es POST (actualizar cantidad)
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (TypeError, ValueError):
            cantidad = 1

        if cantidad > 0:
            item.cantidad = cantidad
            item.save()
        else:
            # Si la cantidad es 0 o negativa, eliminar el item
            item.delete()

    return redirect('ver_carrito')



TALLAS = Talla.objects.all()
COLORES = Color.objects.all()


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Talla, Color
from .forms import ProductoForm

from .models import Producto, Talla, Color

@login_required
def agregar_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        formset = ImagenProductoFormSet(request.POST, request.FILES, queryset=ImagenProducto.objects.none())
        
        if form.is_valid() and formset.is_valid():
            producto = form.save(commit=False)
            producto.creador = request.user
            producto.save()
            form.save_m2m()  # guarda relaciones ManyToMany (tallas, colores)
            
            for imagen_form in formset.cleaned_data:
                if imagen_form and not imagen_form.get('DELETE', False):
                    ImagenProducto.objects.create(
                        producto=producto,
                        imagen=imagen_form['imagen'],
                        color=imagen_form.get('color')
                    )
            
            return redirect('lista_productos')
    else:
        form = ProductoForm()
        formset = ImagenProductoFormSet(queryset=ImagenProducto.objects.none())
    
    return render(request, 'agregar_producto.html', {'form': form, 'formset': formset})






def checkout_view(request):
    if request.method == 'POST':
        # Obtener carrito igual que en ver_carrito
        if request.user.is_authenticated:
            carrito = Carrito.objects.filter(usuario=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            carrito = Carrito.objects.filter(session_key=session_key).first()

        if not carrito or carrito.items.count() == 0:
            return redirect('ver_carrito')  # No hay items, redirige

        # Aquí obtén los datos del formulario: tipo_entrega, direccion, telefono
        tipo_entrega = request.POST.get('tipo_entrega')
        direccion = request.POST.get('direccion') if tipo_entrega == 'envio' else ''
        telefono = request.POST.get('telefono')

        pedido = Pedido.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            tipo_entrega=tipo_entrega,
            direccion=direccion,
            telefono=telefono
        )

        # Copiar los items del carrito al pedido
        for item_carrito in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_carrito.producto,
                talla=item_carrito.talla,
                color=item_carrito.color,
                cantidad=item_carrito.cantidad
            )

        # Limpiar carrito
        carrito.items.all().delete()

        # Redirigir a la página de pago con el pedido creado
        return redirect('pago', pedido_id=pedido.id)

    else:
        # GET muestra el formulario checkout
        # También puedes pasar el carrito y total para mostrar resumen antes de pagar
        return render(request, 'checkout.html')



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

        # Obtener el carrito (de usuario o sesión)
        carrito = obtener_carrito(request)  # Ajusta según tu implementación

        # Crear los items del pedido con los productos del carrito
        for item_carrito in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_carrito.producto,
                talla=item_carrito.talla,
                color=item_carrito.color,
                cantidad=item_carrito.cantidad,
            )

        # Vaciar carrito después de crear pedido
        carrito.items.all().delete()

        return redirect('pago_con_pedido', pedido_id=pedido.id)

    return redirect('checkout')


from django.shortcuts import redirect

def procesar_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        pedido.pagado = True
        pedido.save()
        # Aquí podrías también vaciar el carrito si es necesario
        return redirect('gracias')  # o cualquier otra view

    return redirect('pago_con_pedido', pedido_id=pedido.id)


def gracias_view(request):
    return render(request, 'gracias.html')

def home_view(request):
    # Aquí devuelves el template principal o lo que quieras para la página inicial
    return render(request, 'index.html')


def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    tallas = producto.tallas.all()
    colores = producto.colores.all()
    imagenes = producto.imagenes.all()  # <-- Agregamos esto

    return render(request, "productos/producto_detalle.html", {
        "producto": producto,
        "tallas": tallas,
        "colores": colores,
        "imagenes": imagenes,  # <-- Y lo pasamos al template
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
@login_required
def historial_ventas(request):
    user = request.user

    # Obtener todos los pedidos que tienen al menos un item con producto creado por este admin
    pedidos = Pedido.objects.filter(
        items__producto__creador=user
    ).distinct().prefetch_related('items__producto', 'items__talla', 'items__color')

    # Calcular total para cada pedido
    for pedido in pedidos:
        pedido.total = sum(item.subtotal() for item in pedido.items.all())

    return render(request, 'venta/historial.html', {'pedidos': pedidos})



import openpyxl
from django.http import HttpResponse
from .models import Venta

def exportar_excel(request):
    user = request.user

    # Obtener pedidos que contienen items con productos creados por este admin
    pedidos = Pedido.objects.filter(
        items__producto__creador=user
    ).distinct().prefetch_related('items__producto')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Ventas"

    # Cabeceras
    ws.append(['ID Pedido', 'Producto', 'Cantidad', 'Precio unitario', 'Subtotal', 'Fecha Pedido'])

    for pedido in pedidos:
        fecha_str = pedido.creado.strftime("%Y-%m-%d %H:%M")
        for item in pedido.items.all():
            # Solo exportar items cuyos productos son creados por el admin actual
            if item.producto.creador == user:
                subtotal = item.subtotal()
                precio_unitario = item.producto.precio
                ws.append([
                    pedido.id,
                    item.producto.nombre,
                    item.cantidad,
                    float(precio_unitario),
                    float(subtotal),
                    fecha_str
                    
                ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=historial_ventas.xlsx'
    wb.save(response)
    return response


def pago_view(request, pedido_id=None):
    if pedido_id:
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        # Si quieres, lógica para obtener el pedido más reciente o según sesión
        pedido = None

    if not pedido:
        return redirect('ver_carrito')

    items = pedido.items.select_related('producto', 'talla', 'color').all()
    total = sum(item.subtotal() for item in items)

    context = {
        'pedido': pedido,
        'items': items,
        'total': total
    }
    return render(request, 'pago.html', context)




from django.db import transaction

def crear_pedido_desde_carrito(request):
    if not request.user.is_authenticated:
        # Aquí podrías manejar usuarios anónimos o redirigir al login
        return redirect('login')

    # Obtener el carrito del usuario
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if not carrito or not carrito.items.exists():
        # No hay carrito o está vacío
        return redirect('ver_carrito')

    # Aquí puedes recoger los datos de entrega, teléfono, etc. desde un formulario POST
    # Para ejemplo estático:
    tipo_entrega = 'envio'  # o 'retiro', debe venir de formulario
    direccion = 'Dirección ejemplo'  # debería venir del formulario
    telefono = '123456789'  # del formulario también

    with transaction.atomic():
        pedido = Pedido.objects.create(
            usuario=request.user,
            tipo_entrega=tipo_entrega,
            direccion=direccion,
            telefono=telefono,
        )

        # Copiar items del carrito a pedido
        for item_carrito in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_carrito.producto,
                talla=item_carrito.talla,
                color=item_carrito.color,
                cantidad=item_carrito.cantidad,
            )

        # Vaciar carrito
        carrito.items.all().delete()

    return redirect('pago')  # redirige a la vista donde se muestra el resumen del pedido


from django.views.decorators.http import require_POST

@require_POST
def finalizar_compra(request):
    # Aquí obtienes los datos de entrega del formulario POST
    tipo_entrega = request.POST.get('tipo_entrega')
    direccion = request.POST.get('direccion')
    telefono = request.POST.get('telefono')

    carrito = Carrito.objects.filter(usuario=request.user).first()
    if not carrito or not carrito.items.exists():
        return redirect('ver_carrito')

    with transaction.atomic():
        pedido = Pedido.objects.create(
            usuario=request.user,
            tipo_entrega=tipo_entrega,
            direccion=direccion,
            telefono=telefono,
        )
        for item_carrito in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_carrito.producto,
                talla=item_carrito.talla,
                color=item_carrito.color,
                cantidad=item_carrito.cantidad,
            )
        carrito.items.all().delete()

    return redirect('pago')


def obtener_carrito(request):
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        carrito, created = Carrito.objects.get_or_create(session_key=session_key)
    return carrito



from django.forms import modelformset_factory
from .models import Producto, ImagenProducto

ImagenProductoFormSet = modelformset_factory(
    ImagenProducto,
    fields=('imagen', 'color'),
    extra=3,  # Número de formularios vacíos para subir imágenes nuevas
    can_delete=True  # Permite borrar imágenes en edición
)