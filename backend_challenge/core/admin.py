from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Delivery, Driver, RouteSettings, Trip




@admin.register(RouteSettings)
class RouteSettingsAdmin(OSMGeoAdmin):
    list_display = ("mode", "start_address")


@admin.register(Driver)
class DriverAdmin(OSMGeoAdmin):
    list_display = ("id","name", "capacity",)


@admin.register(Delivery)
class DeliveryAdmin(OSMGeoAdmin):
    list_display = ("id", "code", "address", "weight")


@admin.register(Trip)
class TripAdmin(OSMGeoAdmin):
    list_display = ("id", "code", "driver")


# Register your models here.
