# Generated by Django 5.1.5 on 2025-07-02 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0023_imagenproducto_color_alter_imagenproducto_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorito',
            name='imagen_principal',
            field=models.ImageField(blank=True, null=True, upload_to='favoritos/'),
        ),
    ]
