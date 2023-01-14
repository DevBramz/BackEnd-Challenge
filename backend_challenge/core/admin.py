from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Delivery,Driver,RouteSettings


admin.site.register(Driver)
admin.site.register(RouteSettings)




@admin.register(Delivery)
class DeliveryAdmin(OSMGeoAdmin):
    list_display = ('code','delivery_adress','address')



# Register your models here.
