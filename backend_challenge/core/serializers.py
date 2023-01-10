from django.contrib.auth.models import User
import json
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Customer, Order, RouteSettings, Delivery
from django.core.exceptions import ObjectDoesNotExist
from .Router import CVRP


class RouteSettingsSerializer(serializers.ModelSerializer):
    route_path = serializers.SerializerMethodField()

    class Meta:
        model = RouteSettings
        fields = "__all__"

    def get_route_path(self, obj):
        """returns route route path"""
        deliveries = Delivery.objects.filter(status="pending")
        start = [-1.2841, 36.8155]
        capacity = obj.vehicle_capacity
        # num_drivers=Driver.objects.filter(available=True)
        num_vehicles = obj.num_vehicles
        route = CVRP(num_vehicles, deliveries, start, capacity)  # Route Object

        return route.generate_routes()


class DeliverySerializer(serializers.ModelSerializer):
    cordinates = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = ["id", "code", "address", "cordinates", "status"]

    def get_cordinates(self, obj):
        """Serializer method to return obj location in lat,long"""
        return obj.location


class CustomerProfileUnavailable(APIException):
    """Exception raised when customer profile  is not present in the data."""

    status_code = 404
    default_detail = "Profie could not be found."


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("phone", "code")


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("created", "code", "item", "amount", "status", "customer", "category")

    def create(self, validated_data):
        """
        Create a new Order instance, given the accepted data
        and with the request user
        """
        request = self.context.get("request", None)

        if request is None:
            return False
        # customer=get_object_or_404(Customer, user=user)
        if "customer" not in validated_data:
            try:
                validated_data["customer"] = request.user.customer

            except ObjectDoesNotExist as snip_no_exist:
                raise CustomerProfileUnavailable() from snip_no_exist

        return Order.objects.create(**validated_data)


# }
