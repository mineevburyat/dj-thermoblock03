# Generated by Django 4.2 on 2024-02-12 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_alter_feedback_ip_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feedback',
            options={'verbose_name': 'Обращение', 'verbose_name_plural': 'Обращения'},
        ),
        migrations.AlterField(
            model_name='feedback',
            name='phone',
            field=models.CharField(max_length=12, verbose_name='телефон'),
        ),
    ]