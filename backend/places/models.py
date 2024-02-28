from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(
        verbose_name='Адрес',
        max_length=255,
        unique=True
    )
    lat = models.DecimalField(
        verbose_name='Широта',
        max_digits=9,
        decimal_places=6,
        null=True
    )
    lon = models.DecimalField(
        verbose_name='Долгота',
        max_digits=9,
        decimal_places=6,
        null=True
    )
    registered_at = models.DateField(
        verbose_name='Дата запроса',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Координат места'
        verbose_name_plural = 'Координаты места'

    def __str__(self):
        return self.address
