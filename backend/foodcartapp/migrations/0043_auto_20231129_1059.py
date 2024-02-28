# Generated by Django 3.2.15 on 2023-11-29 10:59

from django.db import migrations


def fill_in_product_price(apps, schema_editor):
    OrderItems = apps.get_model('foodcartapp', 'OrderItem')
    for order_item in OrderItems.objects.all():
        order_item.price = order_item.product.price
        order_item.save(update_fields=['price'])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_orderitem_price'),
    ]

    operations = [
        migrations.RunPython(fill_in_product_price),
    ]
