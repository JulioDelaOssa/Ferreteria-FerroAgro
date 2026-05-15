from django.db import migrations, models
import django.db.models.deletion


def migrar_clientes_existentes(apps, schema_editor):
    Cliente = apps.get_model('inventario', 'Cliente')
    Venta = apps.get_model('inventario', 'Venta')

    for venta in Venta.objects.exclude(cliente_documento__isnull=True).exclude(cliente_documento=''):
        cliente, creado = Cliente.objects.get_or_create(
            documento=venta.cliente_documento,
            defaults={
                'nombre': venta.cliente_nombre or 'Consumidor final',
                'telefono': venta.cliente_telefono,
                'correo': getattr(venta, 'cliente_correo', None),
                'activo': True,
            }
        )
        venta.cliente = cliente
        venta.save(update_fields=['cliente'])


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('documento', models.CharField(max_length=40, unique=True)),
                ('telefono', models.CharField(blank=True, max_length=40, null=True)),
                ('correo', models.EmailField(blank=True, max_length=120, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'db_table': 'clientes',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddField(
            model_name='venta',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ventas', to='inventario.cliente'),
        ),
        migrations.AddField(
            model_name='venta',
            name='cliente_correo',
            field=models.EmailField(blank=True, max_length=120, null=True),
        ),
        migrations.RunPython(migrar_clientes_existentes, migrations.RunPython.noop),
    ]
