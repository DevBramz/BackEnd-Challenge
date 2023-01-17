import string
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


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
        Automatic = "AU", _("Automatic")
        Manual = "MU", _("Manual")

    class Mode(models.TextChoices):
        Distance = "Min_Distance", _("Minimize Distance")
        Arrival = "Ensure Arrival Time", _("Arrival Time")
        minimum_vehicles = "Min_Vehicles", _("Minimum Vehicle") #Focuses more on capacity utilization,uses fewest list(self.deliveries.values_list("weight", flat=True)) vehicles which might travel longer distance

    vehicle_selection = models.CharField(
        max_length=2,
        choices=Utilization.choices,
        default=Utilization.Automatic,
    )
    mode = models.CharField(
        max_length=255,
        choices=Mode.choices,
        default=Mode.Distance,
    )
    # num_vehicles = models.PositiveIntegerField(
    #     default=6,
    # )
    start_address = models.PointField(default=Point(36.798107, -1.283922))
    end_address = models.PointField(default=Point(36.798107, -1.283922))
    
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
    weight = models.PositiveIntegerField(default=1,verbose_name="Quantity/Weight", help_text="For Route Optimization purposes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")
    
    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")

    @property
    def location(self):
        lat = self.delivery_adress.y
        long = self.delivery_adress.x
        location_list = [lat, long]
        location_info = {"adress_name": self.address, "latlong": location_list}
        return location_info

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
    code = models.CharField(max_length=100, blank=True)
    driver = models.CharField(max_length=100, blank=True)

    def save(self, **kwargs):
        if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["edited"]
        if not self.code:
            self.code = generate_secret()

        super().save(**kwargs)

    def __str__(self):
        return str(self.id)
