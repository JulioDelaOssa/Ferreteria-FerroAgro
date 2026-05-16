# FerroAgro Ayapel

Sistema web desarrollado en Django para gestionar productos, inventario, clientes, vendedores, ventas, facturas y reportes de una ferretería/agrotienda.

## Tecnologías

- Python 3.x
- Django 4.2
- PostgreSQL
- HTML
- CSS
- JavaScript
- ReportLab
- OpenPyXL

## Módulos principales

- Login con validación de acceso.
- Registro de usuarios vendedores.
- Recuperación de contraseña con vistas de restablecimiento.
- Dashboard administrativo.
- CRUD de productos.
- CRUD de categorías.
- CRUD de proveedores.
- CRUD de clientes.
- Gestión de vendedores.
- Inventario y movimientos de stock.
- Ventas con factura y validación dinámica de clientes por documento.
- Exportación de reportes en PDF y Excel.
- Breadcrumbs para navegación interna.
- Mensajes dinámicos para acciones importantes.
- Diseño responsive con archivos CSS separados en `static/css`.

## Estructura general

```text
ferreteria/
inventario/
templates/
static/
  css/
  js/
  imagenes/
media/
manage.py
requirements.txt
.env.example
```

## Configuración local

1. Crear y activar un entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Crear una base de datos PostgreSQL llamada `ferroagro_db`.

4. Crear un archivo `.env` tomando como base `.env.example`:

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/ferroagro_db
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=FerroAgro Ayapel <no-reply@ferroagro.local>
```

Con `console.EmailBackend`, los enlaces de recuperacion de contrasena se muestran en la consola donde corre `runserver`. Para enviar correos reales, usa SMTP:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-clave-de-aplicacion
DEFAULT_FROM_EMAIL=FerroAgro Ayapel <tu-correo@gmail.com>
```

5. Ejecutar migraciones:

```bash
python manage.py migrate
```

6. Crear un superusuario:

```bash
python manage.py createsuperuser
```

7. Ejecutar el servidor:

```bash
python manage.py runserver
```

8. Abrir en el navegador:

```text
http://127.0.0.1:8000/
```

## Configuración para despliegue

Para Render u otro servicio compatible con PostgreSQL, configura estas variables de entorno:

```env
SECRET_KEY=clave-segura-de-produccion
DEBUG=False
ALLOWED_HOSTS=tu-dominio.onrender.com,.onrender.com
DATABASE_URL=postgresql://usuario:password@host:puerto/base_de_datos
CSRF_TRUSTED_ORIGINS=https://tu-dominio.onrender.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=FerroAgro Ayapel <no-reply@ferroagro.local>
```

Para produccion, cambia `EMAIL_BACKEND` a `django.core.mail.backends.smtp.EmailBackend` y agrega las variables SMTP del proveedor de correo.

Comandos recomendados para despliegue:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn ferreteria.wsgi:application
```

## Validaciones incluidas

- Campos obligatorios en formularios HTML.
- Validaciones backend en formularios Django.
- Control de stock antes de registrar ventas.
- Validación de cliente por documento en ventas.
- Registro automático de cliente nuevo cuando se usa el botón `+ Nuevo cliente`.
- Mensajes de éxito y error usando el sistema de mensajes de Django.

## Flujo actualizado de ventas

En la pantalla de nueva venta, inicialmente solo se muestra el campo del documento del cliente.

- Si el documento ya existe, se muestra el nombre del cliente en modo lectura y la venta queda asociada a ese cliente.
- Si el documento no existe, aparece el botón `+ Nuevo cliente`.
- Al presionar `+ Nuevo cliente`, aparecen los campos de nombre, teléfono y correo.
- Al guardar la venta, el cliente nuevo se crea en la base de datos y aparece asociado en la factura.

## Revisión antes de entregar

- Ejecutar `python manage.py migrate`.
- Probar login, registro y recuperación de contraseña.
- Probar CRUD de productos, categorías, proveedores, clientes y vendedores.
- Probar ventas y factura.
- Probar movimientos de inventario.
- Probar el panel `/admin` de Django.
- Revisar que `DATABASE_URL` apunte correctamente a PostgreSQL.
- Ejecutar `python manage.py check`.
