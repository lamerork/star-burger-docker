# Generated by Django 3.2.15 on 2023-11-29 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20231129_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Э', 'Электронно'), ('Н', 'Наличностью')], db_index=True, default='Н', max_length=1, verbose_name='способ оплаты'),
        ),
    ]
