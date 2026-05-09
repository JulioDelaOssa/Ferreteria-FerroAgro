import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductoImagen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='productos/')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('producto', models.OneToOneField(db_column='producto_id', on_delete=django.db.models.deletion.CASCADE, related_name='imagen_producto', to='inventario.producto')),
            ],
            options={
                'verbose_name': 'Imagen de producto',
                'verbose_name_plural': 'Imágenes de productos',
                'db_table': 'producto_imagenes',
            },
        ),
        migrations.AddField(
            model_name='venta',
            name='cliente_documento',
            field=models.CharField(blank=True, default='', max_length=40),
        ),
        migrations.AddField(
            model_name='venta',
            name='cliente_nombre',
            field=models.CharField(blank=True, default='Cliente general', max_length=180),
        ),
        migrations.AddField(
            model_name='venta',
            name='cliente_telefono',
            field=models.CharField(blank=True, default='', max_length=40),
        ),
        migrations.AddField(
            model_name='venta',
            name='estado',
            field=models.CharField(choices=[('pagada', 'Pagada'), ('pendiente', 'Pendiente'), ('anulada', 'Anulada')], default='pagada', max_length=30),
        ),
        migrations.AddField(
            model_name='venta',
            name='metodo_pago',
            field=models.CharField(choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia'), ('credito', 'Crédito')], default='efectivo', max_length=30),
        ),
    ]
