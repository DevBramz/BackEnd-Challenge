import string
import textwrap
import uuid

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from fleets.models import Driver
from locations.models import Location

from tuma.common.models import GenericModel

# def set_trip_code() -> str:
#     """Generate a unique trip reference number.

#     Returns:
#         str: The generated reference number.
#     """
#     code = f"TRI-{Trip.objects.count() + 1:04d}"
#     return "TRI-000001" if Trip.objects.filter(code=code).exists() else code


STATUS_PENDING = "pending"
STATUS_AWAITING_ASSIGNMENT = "Awaiting_Assignment"
STATUS_ASSIGNED = "assigned"
# STATUS_DISPATCHED = "dispatched"
STATUS_ONGOING = "ongoing"
STATUS_COMPLETED = "completed"

STATUS_CHOICE = (
    (STATUS_PENDING, _("pending")),
    (STATUS_AWAITING_ASSIGNMENT, _("Awaiting_Assignment")),
    (STATUS_ASSIGNED, _("assigned")),
    # (STATUS_DISPATCHED, _("dispatched")),
    (STATUS_ONGOING, _("ongoing")),
    (STATUS_COMPLETED, _("completed")),
)
TRANSITIONS = (
    {
        STATUS_PENDING: [
            STATUS_ASSIGNED,
        ],
        STATUS_ASSIGNED: [STATUS_ONGOING],
        STATUS_ONGOING: [STATUS_COMPLETED],
        STATUS_COMPLETED: [],
    },
)


class Trip(GenericModel):
    __current_status = None

    code = models.CharField(
        max_length=100, blank=True, unique=True, db_index=True, editable=False
    )
    # trip_code = models.CharField(max_length=100, blank=True, editable=False)
    distance = models.CharField(max_length=100, blank=True, null=True)
    load = models.CharField(max_length=100, blank=True)
    utilization = models.CharField(
        max_length=100, blank=True, null=True, editable=False
    )
    driver = models.ForeignKey(
        Driver, related_name="driver_trips", null=True, on_delete=models.CASCADE
    )
    num_stops = models.CharField(max_length=100, blank=True, default=1, editable=False)
    departure_time = models.DateTimeField(
        blank=True, null=True
    )  # change to planned depature time
    actual_departure_time = models.DateTimeField(blank=True, null=True)
    duration = models.CharField(blank=True, max_length=100, null=True)
    # fuel_consumption = models.PositiveIntegerField(blank=True, null=True)
    estimated_completion_time = models.DateTimeField(blank=True, null=True)
    completed_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="STATUS_PENDING"
    )
   
    class Meta:
        ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__current_status = self.status

    def save(self, *args, **kwargs):
        # allowed_next = TRANSITIONS[self.__current_status]

        # updated = self.status != self.__current_status
        # if self.pk and updated and self.status not in allowed_next:
        #     raise Exception("Invalid transition.", self.status, allowed_next)

        # if self.pk and updated:
        #     self.__current_status = self.status
        if not self.code:
            from .helpers import TripGenerationService

            org_name = self.organization.short_name
            code = TripGenerationService.generate_trip_code(instance=self)
            self.code = org_name.upper() + "-" + code

        return super().save(*args, **kwargs)

    def _transition(self, status):
        self.status = status
        self.save()

    def __str__(self) -> str:
        """
        Returns:
            str: String representation of the trip.
        """
        return self.code

    def get_absolute_url(self) -> str:
        """
        Returns:
            str: The absolute url for the organization.
        """
        return reverse("trip-detail", kwargs={"pk": self.pk})

    # def dispatch(self):
    #     from .tasks import send_sms_driver

    #     # we omit storing the driver on the model for simplicity of the example
    #     message = f"Dear {self.driver.name}, you have been assigned trip {self.code} with {self.num_deliveries} deliveries  ."
    #     self._transition(STATUS_DISPATCHED)
    #     driver_phone = self.driver.phone
    #     send_sms_driver.delay(message, driver_phone)


# class TripTracking(GenericModel):
#     trip = models.ForeignKey(Trip, on_delete=models.CASCADER)
#     driver_location = models.PointField(blank=True)


class OrderVehicle(GenericModel):
    class VehicleTypes(models.TextChoices):
        """
        Vehicle TYPE Choices
        """

        CAR = "CAR", _("Car")
        MOTORCYCLE = " MotorCycle", _("MotorCycle")
        VAN = "VAN", _("Van")
        PICKUP = "PICKUP", _("Pickup")

    vehicle_type = models.CharField(
        max_length=20, choices=VehicleTypes.choices, unique=True
    )
    capacity = models.PositiveSmallIntegerField(verbose_name=_("load capacity"))

    def __str__(self) -> str:
        """
        Returns:
            str: String representation of the trip.
        """
        return self.vehicle_type


class VehicleCharges(GenericModel):
    vehicle = models.OneToOneField(
        OrderVehicle, related_name="vehicle_charges", on_delete=models.CASCADE
    )
    base_charge = models.DecimalField(
        decimal_places=2, max_digits=10, verbose_name=_("Base Charge")
    )
    pickup_charge = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        verbose_name=_("Base Charge"),
    )
    initial_distance = models.PositiveSmallIntegerField(
        verbose_name=_("Initial Distance(Km)")
    )

    amount_per_km = models.PositiveSmallIntegerField(
        verbose_name=_("Amount per extra km")
    )

    def __str__(self) -> str:
        """
        Returns:
            str: String representation of the trip.
        """
        return self.vehicle.vehicle_type

    def get_cost_summary(self, distance):
        total_order_cost = 0
        distance = int(distance)

        if distance <= self.initial_distance:
            total_order_cost = self.base_charge
            return total_order_cost
        else:
            extra_distance = int(distance - self.initial_distance)
            extra_distance_charges = extra_distance * self.amount_per_km
            total_order_cost = self.base_charge + extra_distance_charges
            return total_order_cost


class Order(GenericModel):
    code = code = models.CharField(
        max_length=100, blank=True, unique=True, db_index=True, editable=False
    )
    approved = models.BooleanField(default=False)
    vehicle_type = models.ForeignKey(
        OrderVehicle, related_name="orders", on_delete=models.PROTECT
    )
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        decimal_places=2, max_digits=10, verbose_name=_("Total Amount")
    )

    def save(self, *args, **kwargs):
        from .helpers import generate_order_code

        # org_name = self.organization.short_name

        if not self.code:
            self.code = generate_order_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Returns:
            str: String representation of the trip.
        """
        return self.vehicle_type

    def get_total_order_cost(self):
        vehicle_type = self.vehicle_type

        total_order_cost = 0
        distance = int(self.trip.distance)
        vehicle_type_charges = vehicle_type.vehicle_charges
        if distance <= vehicle_type_charges.initial_distance:
            total_order_cost = vehicle_type_charges.base_charge
            return total_order_cost
        else:
            extra_distance = int(distance - vehicle_type_charges.initial_distance)
            extra_distance_charges = extra_distance * vehicle_type_charges.amount_per_km
            total_order_cost = vehicle_type_charges.base_charge + extra_distance_charges
            return total_order_cost


# class OrderPayment(GenericModel):
#     PAYMENT_STATE_CREATED = "created"
#     PAYMENT_STATE_PENDING = "pending"
#     PAYMENT_STATE_CONFIRMED = "confirmed"
#     PAYMENT_STATE_FAILED = "failed"
#     PAYMENT_STATE_CANCELED = "canceled"
#     PAYMENT_STATE_REFUNDED = "refunded"

#     PAYMENT_STATES = (
#         (PAYMENT_STATE_CREATED, ("payment_state", "created")),
#         (PAYMENT_STATE_PENDING, ("payment_state", "pending")),
#         (PAYMENT_STATE_CONFIRMED, ("payment_state", "confirmed")),
#         (PAYMENT_STATE_CANCELED, ("payment_state", "canceled")),
#         (PAYMENT_STATE_FAILED, ("payment_state", "failed")),
#         (PAYMENT_STATE_REFUNDED, ("payment_state", "refunded")),
#     )
#     Order = models.OneToOneField(
#         Order,
#         related_name="payments",
#         on_delete=models.PROTECT,
#     )
#     payment_state = models.CharField(max_length=190, choices=PAYMENT_STATES)

#     # order = models.ForeignKey(
#     #     Order,
#     #     verbose_name=_("Order"),
#     #     related_name="payments",
#     #     on_delete=models.PROTECT,
#     # )
#     # created = models.DateTimeField(auto_now_add=True)
#     payment_date = models.DateTimeField(null=True, blank=True)


#     get_driver_payment(self)


# info = models.TextField(
#     verbose_name=_("Payment information"), null=True, blank=True
# )
# fee = models.ForeignKey(
#     "OrderFee",
#     null=True,
#     blank=True,
#     related_name="payments",
#     on_delete=models.SET_NULL,
# )
100+50+120+80
