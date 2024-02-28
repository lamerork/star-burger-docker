from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        return self.annotate(
            total_price=Sum(F('item__price')*F('item__quantity'))
        )

    def filter_restaurants_for_order(self, order_id):
        order = self.get(pk=order_id)

        if order.restaurant:
            return Restaurant.objects.filter(pk=order.restaurant.pk).distinct()
        else:
            products = order.item.values_list('product_id', flat=True)
            restaurants = Restaurant.objects.filter(menu_items__product_id__in=products).distinct()

            for product_id in products:
                restaurants = restaurants.filter(menu_items__product_id=product_id)

            return restaurants.distinct()


class Order(models.Model):

    ORDER_STATUSES = [
        ('Н', 'Необработан'),
        ('Г', 'Готовится'),
        ('С', 'Сборка'),
        ('Д', 'Доставка'),
        ('В', 'Выполнен')
     ]

    PAYMENT_METHODS = [
        ('Э', 'Электронно'),
        ('Н', 'Наличностью'),
        ('Е', 'Не указано')
    ]

    status = models.CharField(
        choices=ORDER_STATUSES,
        verbose_name='Cтатус заказа',
        max_length=1,
        default='Е',
        db_index=True
     )

    payment_method = models.CharField(
        verbose_name='Cпособ оплаты',
        choices=PAYMENT_METHODS,
        max_length=1,
        default='Н',
        db_index=True
    )

    firstname = models.CharField(verbose_name='Имя', max_length=50)
    lastname = models.CharField(verbose_name='Фамилия', max_length=50)

    phonenumber = PhoneNumberField(
        db_index=True,
        verbose_name='Телефон',
        region='RU'
        )

    address = models.CharField(verbose_name='Адрес доставки', max_length=100)
    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        null=True,
        blank=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='Ресторан',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )

    registered_at = models.DateTimeField(
        verbose_name='Дата регистрации',
        db_index=True,
        default=timezone.now
    )
    called_at = models.DateTimeField(
        verbose_name='Дата звонка',
        db_index=True,
        null=True,
        blank=True
     )
    delivered_at = models.DateTimeField(
        verbose_name='Дата доставки',
        db_index=True,
        null=True,
        blank=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} - {self.phonenumber}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='item'
        )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='order_item'
        )

    quantity = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        verbose_name='Цена в заказе',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказах'

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'
