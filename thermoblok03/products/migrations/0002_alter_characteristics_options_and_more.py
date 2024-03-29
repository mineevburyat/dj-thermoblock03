# Generated by Django 4.2 on 2024-02-13 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='characteristics',
            options={'verbose_name': 'Характеристика', 'verbose_name_plural': 'Характеристики'},
        ),
        migrations.AlterModelOptions(
            name='mediaproduct',
            options={'verbose_name': 'Медиаресурс', 'verbose_name_plural': 'Медиаресурсы'},
        ),
        migrations.AlterModelOptions(
            name='products',
            options={'verbose_name': 'Продукт', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AlterField(
            model_name='products',
            name='subtitle',
            field=models.CharField(max_length=105, verbose_name='Подзаголовок продукта'),
        ),
    ]
