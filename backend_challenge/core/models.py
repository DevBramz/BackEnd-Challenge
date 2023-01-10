import string
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


def get_number(self):
    return "{0}-{1}".format(str(self.number)[:4], str(self.number)[4:])


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


class Customer(TimeStampedModel):
    phone = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^\+254|07\d{9}$",
                message="Phone number must be entered in the format '+254234567892'. Up to 12 digits allowed with no",
            ),
        ],
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    code = models.CharField("code", max_length=15)

    def __str__(self):
        return str(self.user.email)


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
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    code = models.CharField("code", max_length=15)
    national_id = models.PositiveIntegerField(db_index=True, unique=True)
    name = models.CharField("name", max_length=20)
    capacity = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name


class Order(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELED = "cancelled"
    STATUS_CHOICE = (
        (STATUS_DRAFT, _("draft")),
        (STATUS_PENDING, _("pending")),
        (STATUS_PAID, _("paid")),
        (STATUS_EXPIRED, _("expired")),
        (STATUS_CANCELED, _("cancelled")),
    )
    Funiture = "furniture"
    Electronics = "electronics"
    Fashion = "fashion"
    CATEGORY = [
        (Funiture, _("Furniture")),
        (Electronics, _("electronics")),
        (Fashion, _("fashion")),
    ]
    item = models.CharField("item", max_length=200)
    category = models.CharField(
        max_length=16, choices=CATEGORY, verbose_name=_("Category"), default="fashion"
    )
    amount = models.PositiveIntegerField()
    customer = models.ForeignKey(
        "Customer", related_name="orders", on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=16,
        verbose_name=_("Order code"),
        db_index=True,
        null=True,
        editable=False,
    )
    created = models.CharField(max_length=100, null=True)
    delivery_point = models.PointField()
    address = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="draft")
    # scheduled_at= models.DateTimeField()

    @staticmethod
    def normalize_code(code):
        tr = str.maketrans(
            {
                "2": "Z",
                "4": "A",
                "5": "S",
                "6": "G",
            }
        )
        return code.upper().translate(tr)


    def save(self, **kwargs):
        if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["last_modified"]
        if not self.code:
            self.code = generate_secret()
        if not self.created:
            timecreated = self.added.strftime("%Y-%m-%d-%H:%M")
            self.created = timecreated

        super().save(**kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-added"]


class RouteSettings(TimeStampedModel):
    class Utilization(models.TextChoices):
        Automatic = "AU", _("Automatic")
        Manual = "MU", _("Manual")

    class Mode(models.TextChoices):
        Distance = "Minimum Distance", _("Min Distance")
        Arrival = "Ensure Arrival Time", _("Arrival Time")
        Balance = "Balance Distance and Arrival Times ", _("Balance Distance and Arrival Time")

    vehicle_utilization = models.CharField(
        max_length=2,
        choices=Utilization.choices,
        default=Utilization.Automatic,
    )
    mode = models.CharField(
        max_length=255,
        choices=Mode.choices,
        default=Mode.Distance,
    )
    vehicle_capacity = models.PositiveIntegerField(
        default=2,
    )
    num_vehicles = models.PositiveIntegerField(
        default=6,
    )
    start_address = models.PointField(default=Point(36.798107, -1.283922))
    end_address = models.PointField(default=Point(36.798107, -1.283922))

    def __str__(self):
        return str(self.id)


class Delivery(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_DElIVERED = "delivered"
    STATUS_CHOICE = (
        (STATUS_DRAFT, _("draft")),
        (STATUS_PENDING, _("pending")),
        (STATUS_DElIVERED, _("delivered")),
    )
    code = models.CharField(max_length=100, blank=True)
    delivery_adress = models.PointField()
    address = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")

    @property
    def location(self):
        lat = self.delivery_adress.y
        long = self.delivery_adress.x
        location_list = [lat, long]
        return location_list

    def save(self, **kwargs):
        if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["last_modified"]
        if not self.code:
            self.code = generate_secret()

        super().save(**kwargs)

    def __str__(self):
        return str(self.code)

   
