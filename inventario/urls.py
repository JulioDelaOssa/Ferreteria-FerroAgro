from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='dashboard'),
    path('redirigir/', views.post_login, name='post_login'),
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/editar/<int:producto_id>/', views.producto_editar, name='producto_editar'),
    path('productos/eliminar/<int:producto_id>/', views.producto_eliminar, name='producto_eliminar'),
    path('inventario/', views.inventario_lista, name='inventario_lista'),
    path('inventario/ajustar/<int:producto_id>/', views.ajustar_stock, name='ajustar_stock'),
    path('ventas/', views.ventas_panel, name='ventas_panel'),
    path('ventas/producto/<int:producto_id>/', views.venta_crear, name='venta_crear'),
    path('vendedores/', views.vendedores_lista, name='vendedores_lista'),
    path('vendedores/nuevo/', views.vendedor_crear, name='vendedor_crear'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
]