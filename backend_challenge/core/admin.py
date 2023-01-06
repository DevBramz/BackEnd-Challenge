from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Customer, Order,Delivery

admin.site.register(Customer)

@admin.register(Order)
class OrderAdmin(OSMGeoAdmin):
    list_display = ('code',)
@admin.register(Delivery)
class DeliveryAdmin(OSMGeoAdmin):
    list_display = ('code', 'delivery_adress','address','location')

# Register your models here.
