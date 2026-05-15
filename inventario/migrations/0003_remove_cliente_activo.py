from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_cliente_venta_cliente_correo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='activo',
        ),
    ]
