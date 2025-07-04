# Generated by Django 5.1.5 on 2025-06-23 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0012_alter_itemcarrito_color_alter_itemcarrito_talla'),
    ]

    operations = [
        migrations.CreateModel(
            name='MensajeContacto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('asunto', models.CharField(max_length=150)),
                ('mensaje', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
