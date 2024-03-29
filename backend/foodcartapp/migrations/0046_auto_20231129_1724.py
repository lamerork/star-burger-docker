# Generated by Django 3.2.15 on 2023-11-29 14:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20231129_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата звонка'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='registered_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата регистрации'),
        ),
    ]
