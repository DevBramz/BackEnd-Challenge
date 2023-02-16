from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Delivery, Driver, RouteSettings, Trip,Vehicle,Organization,Hub


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass
@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    pass



@admin.register(RouteSettings)
class RouteSettingsAdmin(OSMGeoAdmin):
    list_display = ("id","selection", "start_address")
@admin.register(Vehicle)
class Vehicle(OSMGeoAdmin):
    list_display = ("id", "no_plate", "driver", )


@admin.register(Driver)
class DriverAdmin(OSMGeoAdmin):
    list_display = (
        "id",
        "name",
        "capacity",
    )


@admin.register(Delivery)
class DeliveryAdmin(OSMGeoAdmin):
    list_display = ("id", "code", "address", "weight")



@admin.register(Trip)
class TripAdmin(OSMGeoAdmin):
    list_display = (
        "id",
        "code",
        "driver",
        "num_deliveries",
        "load",
        "utilization",
        "distance",
        "depature_time",

        
        
    )


# Register your models here.
