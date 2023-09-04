from django.contrib import admin
from trips.models import OrderVehicle, Trip, VehicleCharges

# Register your models here.


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderVehicle)
class OrderVehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleCharges)
class VehicleChargesAdmin(admin.ModelAdmin):
    pass


# Register your models here.
