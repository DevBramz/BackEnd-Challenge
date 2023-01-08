from django.contrib.auth.models import User
import json
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Customer, Order, OrderShipment, RouteSettings, Delivery
from django.core.exceptions import ObjectDoesNotExist
from .tsm import Route


class RouteSettingsSerializer(serializers.ModelSerializer):
    route_path = serializers.SerializerMethodField()

    class Meta:
        model = RouteSettings
        fields = "__all__"

    def get_route_path(self, obj):
        deliveries = Delivery.objects.filter(status="pending")
        print(deliveries.count)
        adress = obj.start_address
        start = (-1.2841,36.8155)
        adress2 = obj.end_address
        end = (adress2.y, adress2.x)
        # locations = [
        #     (-1.393864, 36.744238),  # RONGAI
        #     (-1.205604, 36.779606),  # RUAKA
        #     (-1.283922, 36.798107),  # Kilimani
        #     (-1.366859, 36.728069),  # langata
        #     (-1.311752, 36.698598),  # karen1 
        #     (-1.3362540729230734, 36.71637587249404), # karen2
        #     (-1.1752106333542798, 36.75964771015464),  # Banana1
        #     (-1.1773237686269944, 36.760334355612045),  # Banana2
        # ]  #
        
        locations=[delivery.location for delivery in deliveries]
    

        # for delivery in deliveries:
        #     locations.append(delivery.location)
        # print(locations)

        route = Route(4, deliveries, start, 15, locations)

        return route.generate_routes()


# create a tuple


class DeliverySerializer(serializers.ModelSerializer):
    cordinates = serializers.SerializerMethodField()
    class Meta:
        model = Delivery
        fields = ["id", "code", "address","cordinates","status"]
        
    def get_cordinates(self,obj):
        return obj.location


class CustomerProfileUnavailable(APIException):
    """Exception raised when customer profile  is not present in the data."""

    status_code = 404
    # default_detail = 'Service temporarily unavailable, try again later.'


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

    # class OrderShipmentSerializer(serializers.HyperlinkedModelSerializer):
    #     class Meta:
    #         model = OrderShipment
    #         fields = (
    #             "created",
    #             "code",
    #             "item",
    #             "amount",
    #             "status",
    #             "customer",
    #             "category",
    #         )

    # def create(self, validated_data):
    #     """
    #     Create a new Order instance, given the accepted data
    #     and with the request user
    #     """
    #     request = self.context.get("request", None)

    #     if request is None:
    #         return False
    #     # customer=get_object_or_404(Customer, user=user)
    #     if "customer" not in validated_data:
    #         try:
    #             validated_data["customer"] = request.user.customer

    #         except ObjectDoesNotExist as snip_no_exist:
    #             raise CustomerProfileUnavailable() from snip_no_exist

    #     return Order.objects.create(**validated_data)

    # from django.db import models


# STATE_CREATED = "created"
# STATE_ = ""
# STATE_TO_AIRPORT = "to_airport"
# STATE_TO_HOTEL = "to_hotel"
# STATE_DROPPED_OFF = "dropped_off"


#     0 - created
#     1 - assigned
#     2 - on_the_way
#     3 - checked_in
#     4 - done
#     5 - this status is not in use
#     6 - accepted
#     7 - canceled
#     8 - rejected
#     9 - unacknowledged


# STATE_CHOICES = (
#     (STATE_REQUEST, STATE_REQUEST),
#     (STATE_WAITING, STATE_WAITING),
#     (STATE_TO_AIRPORT, STATE_TO_AIRPORT),
#     (STATE_TO_HOTEL, STATE_TO_HOTEL),
#     (STATE_DROPPED_OFF, STATE_DROPPED_OFF),
# )

# TRANSITIONS = {
#     STATE_REQUEST: [STATE_WAITING,],
#     STATE_WAITING: [STATE_REQUEST, STATE_TO_AIRPORT],
#     STATE_TO_AIRPORT: [STATE_TO_HOTEL, STATE_REQUEST],
#     STATE_TO_HOTEL: [STATE_DROPPED_OFF],
#     STATE_DROPPED_OFF: [],
# }


# class Pickup(models.Model):
#     __current_state = None

#     state = models.CharField(
#         max_length=20, choices=STATE_CHOICES, default=STATE_REQUEST
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.__current_state = self.state

#     def save(
#         self,
#         force_insert=False,
#         force_update=False,
#         using=None,
#         update_fields=None,
#     ):
#         allowed_next = TRANSITIONS[self.__current_state]

#         updated = self.state != self.__current_state
#         if self.pk and updated and self.state not in allowed_next:
#             raise Exception("Invalid transition.", self.state, allowed_next)

#         if self.pk and updated:
#             self.__current_state = self.state

#         return super().save(
#             force_insert=force_insert,
#             force_update=force_update,
#             using=using,
#             update_fields=update_fields,
#         )

#     def _transition(self, state):
#         self.state = state
#         self.save()

#     def assign(self, driver):
#         # we omit storing the driver on the model for simplicity of the example
#         self._transition(STATE_WAITING)

#     def accept(self):
#         self._transition(STATE_TO_AIRPORT)

#     def decline(self):
#         self._transition(STATE_REQUEST)

#     def picked_up(self):
#         self._transition(STATE_TO_HOTEL)

#     def dropped_off(self):
#         self._transition(STATE_DROPPED_OFF)
# class User(AbstractUser):
#     photo = models.ImageField(upload_to='photos', null=True, blank=True)

#     @property
#     def group(self):
#         groups = self.groups.all()
#         return groups[0].name if groups else None


# def get_or_assign_number(self):
#         if self.number is None:
#             epoch = datetime.now().date()
#             epoch = epoch.replace(epoch.year, 1, 1
#             qs = Order.objects.filter(number__isnull=False, created_at__gt=epoch)
#             qs = qs.aggregate(models.Max('number'))
#             try:
#                 epoc_number = int(str(qs['number__max'])[4:]) + 1
#                 self.number = int('{0}{1:05d}'.format(epoch.year, epoc_number))
#             except (KeyError, ValueError):
#                 # the first order this year
#                 self.number = int('{0}00001'.format(epoch.year))
#         return self.get_number(){
# "destinations": ["(41.878876, -87.635918)","(41.8848274, -87.6320859)"]


def restore_object(self, attrs, instance=None):
    if instance:
        # Update existing instance
        instance.title = attrs.get("title", instance.title)
        instance.code = attrs.get("code", instance.code)
        instance.linenos = attrs.get("linenos", instance.linenos)
        instance.language = attrs.get("language", instance.language)
        instance.style = attrs.get("style", instance.style)
        return instance

    # Create new instance
    return Snippet(**attrs)


# }
