# Generated by Django 4.2 on 2024-02-14 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_characteristics_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='slug',
            field=models.SlugField(default='tb300'),
        ),
    ]
