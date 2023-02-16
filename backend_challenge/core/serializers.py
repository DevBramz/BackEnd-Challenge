from django.contrib.auth.models import User
import json
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Driver, RouteSettings, Delivery, Trip
from django.core.exceptions import ObjectDoesNotExist
from .Router import CVRP
from .utilization import LoadOptimization
from django.db.models import Q


class RouteSettingsSerializer(serializers.ModelSerializer):
    # routes_data = serializers.SerializerMethodField()

    class Meta:
        model = RouteSettings
        fields = [ "selection","start_location", "end_location","departure_time","finish_time",]

    
class TripSerializer(serializers.ModelSerializer):
       
    # routes_data = serializers.SerializerMethodField()
    driver_capacity= serializers.SerializerMethodField()
    driver= serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [ "id", "code","status", "driver","num_deliveries","load","utilization","distance","driver_capacity","depature_time",]\
            
        
    def get_driver_capacity(self, obj):
        """Serializer method to return obj location in lat,long"""
        return obj.driver.capacity
    
    def get_driver(self, obj):
        """Serializer method to return obj location in lat,long"""
        return obj.driver.name
        


class DeliverySerializer(serializers.ModelSerializer):
    cordinates = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = [
            "id",
            "code",
            "phone",
            "address",
            "cordinates",
            "status",
            "weight",
        ]

    def get_cordinates(self, obj):
        """Serializer method to return obj location in lat,long"""
        return obj.location


class ContactForm(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField()

    def save(self):
        email = self.validated_data["email"]
        message = self.validated_data["message"]


# class DriverListSerializer(serializers.ListSerializer):

#     """Enables bulk updtae

#     Returns:
#         _type_: _
#     """

#     def update(self, instance, validated_data):
#         """Enables bulk updtae

#         """

#         # Maps for id->instance and id->data item.
#         driver_mapping = {driver.id: driver for driver in instance}
#         data_mapping = {item["id"]: item for item in validated_data}

#         # Perform creations and updates.
#         ret = []
#         for driver_id, data in data_mapping.items():
#             driver = driver_mapping.get(driver_id, None)
#             ret.append(self.child.update(driver, data))

#         # Perform deletions.
#         for driver_id, driver in driver_mapping.items():
#             if driver_id not in data_mapping:
#                 driver.delete()

#         return ret


# class driverSerializer(serializers.Serializer):
#     # We need to identify elements in the list using their primary key,
#     # so use a writable field here, rather than the default which would be read-only.
#     id = serializers.IntegerField()
#     ...

#     class Meta:
#         list_serializer_class = driverListSerializer


# class UpdateListSerializer(serializers.ListSerializer):

#     def update(self, instances, validated_data):

#         instance_hash = {index: instance for index, instance in enumerate(instances)}

#         result = [
#             self.child.update(instance_hash[index], attrs)
#             for index, attrs in enumerate(validated_data)
#         ]

#         return result

# class EventSerializer(serializers.Serializer):
#     description = serializers.CharField(max_length=100)
#     start = serializers.DateTimeField()
#     finish = serializers.DateTimeField()

#     def validate(self, data):
#         """
#         Check that start is before finish.
#         """
#         if data['start'] > data['finish']:
#             raise serializers.ValidationError("finish must occur after start")
#         return data


#  def post(self, request, *args, **kwargs):
#         order_items = {
#             'items': []
#         }

#         items = request.POST.getlist('items[]')

#         for item in items:
#             menu_item = MenuItem.objects.get(pk__contains=int(item))
#             item_data = {
#                 'id': menu_item.pk,
#                 'name': menu_item.name,
#                 'price': menu_item.price
#             }

#             order_items['items'].append(item_data)

#             price = 0
#             item_ids = []

#         for item in order_items['items']:
#             price += item['price']
#             item_ids.append(item['id'])

#         order = OrderModel.objects.create(price=price)
#         order.items.add(*item_ids)

#         context = {
#             'items': order_items['items'],
#             'price': price
#         }

#         return render(request, 'customer/order_confirmation.html', context)
# https://avlview.com/schedule-trips/
# https://en.wikipedia.org/wiki/GPS_tracking_unit
# https://en.wikipedia.org/wiki/Vehicle_tracking_system
# https://en.wikipedia.org/wiki/Fleet_management
# https://avlview.com/fleet-management/
