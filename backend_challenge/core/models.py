import string
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
import datetime


def generate_secret():

    initial = "DEL"
    code = get_random_string(
        length=6, allowed_chars=string.ascii_lowercase + string.digits
    )

    full_code = initial + code
    return full_code.upper()


class TimeStampedModel(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Driver(TimeStampedModel):
    phone = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^\+254\d{9}$",
                message="Phone number must be entered in the format '+254234567892'. Up to 12 digits allowed with no",
            ),
        ],
    )
    national_id = models.PositiveIntegerField(db_index=True, unique=True)
    name = models.CharField("name", max_length=20)
    capacity = models.PositiveIntegerField(null=True)
    availability_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Vehicle(TimeStampedModel):
    state = models.BooleanField(default=True)

    no_plate = models.CharField(max_length=15, verbose_name="No Plate", unique=True)

    allocated_to = models.ForeignKey(
        "Driver", related_name="drivers", on_delete=models.CASCADE
    )
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return str(self.no_plate)


class RouteSettings(TimeStampedModel):
    class Utilization(models.TextChoices):

        Distance = "Min_Distance", _(
            "Balance Distance and Vehicle Utilization"
        )  # Finds a balance between distance and capacities available

        minimum_vehicles = "Min_Veh", _(
            "Minimum Vehicle"
        )  # Focuses more on capacity utilization,uses fewest vehicles which might travel longer distance

        Manual = "MU", _("Manual")

    # class Mode(models.TextChoices):
    #     Distance = "Min_Distance", _("Minimize Distance")
    #     Arrival = "Ensure Arrival Time", _("Arrival Time")
    #     minimum_vehicles = "Min_Vehicles", _("Minimum Vehicle")

    selection = models.CharField(
        max_length=255,
        choices=Utilization.choices,
        default=Utilization.Distance,
        verbose_name="Vehicle Selection",
    )

    # num_vehicles = models.PositiveIntegerField(
    #     default=6,
    # )
    avoid_highways = models.BooleanField(null=True)
    start_address = models.PointField(default=Point(36.798107, -1.283922))
    end_address = models.PointField(default=Point(36.798107, -1.283922))
    depature_time = models.TimeField(auto_now=True)
    finish_time = models.TimeField(blank=True, null=True)
    service_time=models.TimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("RouteSettings")
        verbose_name_plural = _("RouteSettings")

    def __str__(self):
        return str(self.id)


class Delivery(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_ASSIGNED = "assigned"
    STATUS_DElIVERED = "delivered"
    STATUS_CHOICE = (
        (STATUS_DRAFT, _("draft")),
        (STATUS_PENDING, _("pending")),
        (STATUS_DElIVERED, _("delivered")),
        (STATUS_ASSIGNED, _("assigned")),
    )
    code = models.CharField(max_length=100, blank=True)
    delivery_adress = models.PointField()
    address = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^\+254\d{9}$",
                message="Phone number must be entered in the format '+254234567892'. Up to 12 digits allowed with no",
            ),
        ],
    )
    weight = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantity/Weight",
        help_text="For Route Optimization purposes",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")
    earliest = models.TimeField(blank=True, null=True)
    latest = models.TimeField(blank=True, null=True)
    trip = models.ForeignKey(
        "Trip",
        related_name="trip_deliveries",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")

    @property
    def location(self):
        lat = self.delivery_adress.y
        long = self.delivery_adress.x
        location_list = [lat, long]
        location_info = {
            "code": self.code,
            "adress_name": self.address,
            "latlong": location_list,
        }
        return location_info

    # @property
    # def clone(self):
    #     """Serializer method to clone """
    #     return reverse("core:delivery-clone", args=[self.id])

    def save(self, **kwargs):
        if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["edited"]
        if not self.code:
            self.code = generate_secret()

        super().save(**kwargs)

    #         # we omit storing the driver on the model for simplicity of the example
    #         self._transition(STATE_WAITING)

    def assign(self, driver):
        #         # we omit storing the driver on the model for simplicity of the example
        #         self._transition(STATE_WAITING)

        self.status = "assigned"
        self.save(update_fields=["status"])

    def __str__(self):
        return str(self.id)


class Trip(TimeStampedModel):
    code = models.CharField(max_length=100, blank=True,editable=False)
    # driver = models.CharField(max_length=100, blank=True)
    distance = models.CharField(max_length=100, blank=True, null=True)
    load = models.CharField(max_length=100, blank=True)
    utilization = models.CharField(max_length=100, blank=True,editable=False)
    rider = models.ForeignKey(
        "Driver", related_name="driver_trips", null=True, on_delete=models.CASCADE
    )
    num_deliveries= models.CharField(max_length=100, blank=True,default=1,editable=False)
    depature_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
    
    @property
    def trip_deliveries(self):
        # lat = self.delivery_adress.y
        # long = self.delivery_adress.x
        # location_list = [lat, long]
        # location_info = {
        #     "code": self.code,
        #     "adress_name": self.address,
        #     "latlong": location_list,
        trip_deliveries=Delivery.objects.filter(trip=self).count()
        
        print(trip_deliveries)
        return trip_deliveries

    # duration=models.CharField(max_length=100, blank=True)

    # driver = models.ForeignKey(
    #     Driver,
    #     related_name='trips_assigned',
    #     blank=True,
    #     null=True,

    # )

    def save(self, **kwargs):
        if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["edited"]
        if not self.code:
            self.code = generate_secret()

        super().save(**kwargs)

    def __str__(self):
        return str(self.code)

    # Routes are created which minimize the total number of miles driven by your workers.
    # This will reduce the overall cost to complete the route,
    # however, it allows for violations in your Complete Before and Complete After windows.
    # however, it allows for violations in your Complete Before and Complete After windows.
    # however, it allows for violations in your Complete Before and Complete After windows.
    # however, it allows for violations in your Complete Before and Complete After windows.
    #  https://stackoverflow.com/questions/36500331/putting-latitudes-and-longitudes-into-a-distance-matrix-google-map-api-in-pytho
    # https://gist.github.com/Kevin-De-Koninck/bafceafe1ed16784962a689b3a90f0c4


#     To avoid any issue with rounding, you can scale the distance matrix: multiply all entries of the matrix by a large number — say 100. This multiplies the length of any route by a factor of 100, but it doesn't change the solution. The advantage is that now when you round the matrix entries, the rounding amount (which is at most 0.5), is very small compared to the distances, so it won't affect the solution significantly.

# If you scale the distance matrix, you also need to change the solution printer to divide the scaled route lengths by the scaling factor, so that it displays the unscaled distances of the routes.
# Maximum tasks per driver.https://www.traccar.org/
