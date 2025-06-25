"""
URL configuration for productos_clinicos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from productos import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from productos.views import exportar_excel



urlpatterns = [
    path('admin/', admin.site.urls),  # <--- Esta línea habilita el admin
    path('', views.lista_productos, name='lista_productos'),

    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('login/', views.login_personalizado, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('index/', views.index, name='index'),
    path('hombre/', views.productos_hombre, name='hombre'),
    path('mujer/', views.productos_mujer, name='mujer'),
    path('editar/<int:producto_id>/',
         views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/',
         views.eliminar_producto, name='eliminar_producto'),
    path('marcas/', views.marcas, name='marcas'),
    path('login/', views.login_personalizado, name='login'),
    path('usuario/', views.panel_usuario, name='panel_usuario'),
    path('admin_custom/', views.admin_custom, name='admin_custom'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('accesorios/', views.productos_accesorio, name='accesorios'),
    path('favorito/<int:producto_id>/',
         views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/<int:item_id>/',
         views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/actualizar/<int:item_id>/',
         views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('agregar/<int:producto_id>/',
         views.agregar_al_carrito, name='agregar_al_carrito'),
    path('base/', views.base, name='base'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/procesar/', views.procesar_checkout, name='procesar_checkout'),
    path('pago/', views.pago_view, name='pago_sin_pedido'),

    path('gracias/', views.gracias_view, name='gracias'),
    path('', views.home_view, name='home'),
    path('producto/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('productos/hombre/', views.lista_productos_hombre, name='productos_hombre'),
    path('productos/mujer/', views.lista_productos_mujer, name='productos_mujer'),
    path('mis-ventas/', views.historial_ventas, name='historial_ventas'),
    path('exportar-excel/', exportar_excel, name='exportar_excel'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('pago/<int:pedido_id>/', views.pago_view, name='pago_con_pedido'),
    path('pago/<int:pedido_id>/', views.pago_view, name='pago'),  # para pago con pedido
    path('pago/procesar/<int:pedido_id>/', views.procesar_pago, name='procesar_pago'),

    


    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
