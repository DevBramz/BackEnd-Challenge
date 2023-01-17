from django.contrib.auth.models import User
import json
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Driver, RouteSettings, Delivery
from django.core.exceptions import ObjectDoesNotExist
from .Router import CVRP
from .utilization import Packing


class RouteSettingsSerializer(serializers.ModelSerializer):
    routes_data = serializers.SerializerMethodField()

    class Meta:
        model = RouteSettings
        fields = "__all__"

    def get_routes_data(self, obj):
        """returns route route path"""
        deliveries = Delivery.objects.filter(
            status="pending"
        )  # using this for now but would need to use the selected deliveries from datatable

        # start = [
        #     -1.2841,
        #     36.8155,
        # ]  # using this for now but would need to use teamhub adress from form data

        # num_drivers=Driver.objects.filter(available=True)
        start = [
            -1.2951239,
            # kilimani business center
            36.7815907,
        ]  # using this for now but would need to use teamhub adress from form data
        all_drivers = Driver.objects.all()

        if obj.selection == "Min_Distance":
            drivers = all_drivers
        #    print(drivers)
        else:
            obj.selection == "Min_Veh"
            Packed = Packing(deliveries, all_drivers)
            list_of_ids = Packed.main()

            # driverlot=[all_drivers[i] for i in driver_indexes]
            drivers = all_drivers.filter(pk__in=list_of_ids)
            print(drivers)
        route = CVRP(
            drivers,
            deliveries,
            start,
        )  # Route Object

        return route.generate_routes()


class DeliverySerializer(serializers.ModelSerializer):
    cordinates = serializers.SerializerMethodField()
   
    class Meta:
        model = Delivery
        fields = ["id", "code", "address", "cordinates", "status", "weight",]

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
