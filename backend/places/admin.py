from django.contrib import admin

from .models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
        'lat',
        'lon',
        'registered_at',
    ]
    list_filter = [
        'address',
        'registered_at',
    ]
    list_display = [
        'address',
        'lat',
        'lon',
        'registered_at',
    ]