# FerroAgro Ayapel

Sistema web desarrollado en Django para la gestion de inventario, productos y reportes de una ferreteria/agrotienda.

## Tecnologias

- Python 3.x
- Django
- SQLite
- HTML
- CSS

## Modulos principales

- Gestion de productos.
- Gestion de inventario.
- Busqueda y consulta de informacion.
- Reportes basicos.
- Exportacion de reportes a Excel y PDF.

## Instalacion

1. Clonar el repositorio:

    git clone URLREPO

2. Entrar a la carpeta del proyecto:

    cd FerroAgroAyapel

3. Crear entorno virtual:

    python -m venv venv

4. Activar entorno virtual en Windows:

    venv\Scripts\activate

5. Instalar dependencias:

    pip install -r requirements.txt

6. Ejecutar migraciones:

    python manage.py migrate

7. Iniciar servidor:

    python manage.py runserver

8. Abrir en el navegador:

    http://127.0.0.1:8000/

## Uso basico

El sistema permitira gestionar productos e inventario de una ferreteria/agrotienda.

Desde la aplicacion se podran realizar acciones como:

- Registrar productos.
- Consultar productos disponibles.
- Actualizar informacion de productos.
- Controlar cantidades en inventario.
- Buscar productos.
- Generar reportes basicos.