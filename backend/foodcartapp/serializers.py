from rest_framework.serializers import ModelSerializer
from django.shortcuts import get_object_or_404

from phonenumber_field.serializerfields import PhoneNumberField

from .models import Order, OrderItem, Product


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    phonenumber = PhoneNumberField()

    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )

        for item in validated_data['products']:
            product = get_object_or_404(Product, name=item['product'])
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=product.price
            )

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']