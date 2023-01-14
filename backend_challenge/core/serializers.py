from django.contrib.auth.models import User
import json
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import  Driver,RouteSettings, Delivery
from django.core.exceptions import ObjectDoesNotExist
from .Router import CVRP


class RouteSettingsSerializer(serializers.ModelSerializer):
    route_path = serializers.SerializerMethodField()

    class Meta:
        model = RouteSettings
        fields = "__all__"

    def get_route_path(self, obj):
        """returns route route path"""
        deliveries = Delivery.objects.filter(
            status="assigned"
        )  # using this for now but would need to use the selected deliveries from datatable

        start = [
            -1.2841,
            36.8155,
        ]  # using this for now but would need to use teamhub adress from form data

        # num_drivers=Driver.objects.filter(available=True)
        drivers=Driver.objects.all()
        route = CVRP(drivers, deliveries, start,)  # Route Object

        return route.generate_routes()


class DeliverySerializer(serializers.ModelSerializer):
    cordinates = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = ["id", "code", "address", "cordinates", "status"]

    def get_cordinates(self, obj):
        """Serializer method to return obj location in lat,long"""
        return obj.location








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
