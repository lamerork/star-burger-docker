import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order
from places.models import Place

from geopy import distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(address):

    place, create = Place.objects.get_or_create(address=address)

    if create:

        try:
            base_url = "https://geocode-maps.yandex.ru/1.x"
            response = requests.get(base_url, params={
                "geocode": address,
                "apikey": settings.YANDEX_MAP_API,
                "format": "json",
            })

            response.raise_for_status()
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']

            if not found_places:
                return None

            most_relevant = found_places[0]
            place.lon, place.lat  = most_relevant['GeoObject']['Point']['pos'].split(" ")

            place.save()

        except (HTTPError, Timeout, ConnectionError):
            return None

    return place.lon, place.lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    order_items = Order.objects.exclude(status='В').total_price().order_by('-id')

    for order_item in order_items:
        order_item.restaurants = Order.objects.filter_restaurants_for_order(order_item.id)
        order_coordinates = fetch_coordinates(order_item.address)
        for restauran in order_item.restaurants:
            restauran_coordinates = fetch_coordinates(restauran.address)

            if order_coordinates and restauran_coordinates:
                restauran.distance = round(distance.distance(order_coordinates, restauran_coordinates).kilometers, 2)
            else:
                restauran.distance = 'Ошибка определения координат'

        order_item.restaurants = sorted(order_item.restaurants, key=lambda x: x.distance)

    return render(request, template_name='order_items.html', context={
        'order_items': order_items,
    })
