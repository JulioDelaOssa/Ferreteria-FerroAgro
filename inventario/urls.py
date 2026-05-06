from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='dashboard'),
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/editar/<int:producto_id>/', views.producto_editar, name='producto_editar'),


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