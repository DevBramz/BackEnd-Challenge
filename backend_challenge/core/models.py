import string
import uuid
import textwrap
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.crypto import get_random_string

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models import PointField

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import Group


import datetime


def generate_secret():

    initial = "DEL"
    code = get_random_string(
        length=6, allowed_chars=string.ascii_lowercase + string.digits
    )

    full_code = initial + code
    return full_code.upper()

def get_organization_hubs():
    
    org=Organization.objects.get(org__name="ibuQA")
    hubs=org.hubs.all()
    choices=[(o.name, str(o)) for o in hubs]
    print(hubs)
    print((choices))
    return choices



    
    

def generate_trip_secret():

    initial = "SHI"
    code = get_random_string(
        length=6, allowed_chars=string.ascii_lowercase + string.digits
    )

    full_code = initial + "-"+code
    return full_code.upper()

def set_trip_code() -> str:
        """Generate a unique trip reference number.

        Returns:
            str: The generated reference number.
        """
        code = f"TRI-{Trip.objects.count() + 1:04d}"
        return (
            "TRI-000001"
            if Trip.objects.filter(code=code).exists()
            else code
        )
class Employee(models.Model):
    employee_title = models.ManyToManyField(Group)

class TimeStampedModel(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Organization(TimeStampedModel):
    """
    Organization Model Fields
    """

    
    class OrganizationTypes(models.TextChoices):
        """
        Organization Type Choices
        """

        ASSET = "Asset", _("Asset")
        BROKERAGE = "Brokerage", _("Brokerage")
        BOTH = "Both", _("Both")

    # @final
    # class LanguageChoices(models.TextChoices):
    #     """
    #     Supported Language Choices for Monta
    #     """

    #     ENGLISH = "en", _("English")
    #     SPANISH = "es", _("Spanish")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    name = models.CharField(
        _("Organization Name"),
        max_length=255,
    )
    scac_code = models.CharField(
        max_length=4,
        verbose_name=_("SCAC Code"),
        help_text=_("The SCAC code for the organization."),
    )
    org_type = models.CharField(
        max_length=10,
        choices=OrganizationTypes.choices,
        default=OrganizationTypes.ASSET,
        verbose_name=_("Organization Type"),
        help_text=_("The type of organization."),
    )
    # timezone = models.CharField(
    #     _("Timezone"),
    #     max_length=255,
    #     default="America/New_York",
    #     help_text=_("The timezone of the organization"),
    #     validators=[validate_org_timezone],
    # )
    # language = models.CharField(
    #     _("Language"),
    #     max_length=2,
    #     choices=LanguageChoices.choices,
    #     default=LanguageChoices.ENGLISH,
    #     help_text=_("The language of the organization"),
    # )
    currency = models.CharField(
        _("Currency"),
        max_length=255,
        default="USD",
        help_text=_("The currency that the organization uses"),
    )
    # date_format = models.CharField(
    #     _("Date Format"),
    #     max_length=255,
    #     default="MM/DD/YYYY",
    #     help_text=_("Date Format"),
    # )
    # time_format = models.CharField(
    #     _("Time Format"),
    #     max_length=255,
    #     default="HH:mm",
    #     help_text=_("Time Format"),
    # )
    # logo = models.ImageField(
    #     _("Logo"), upload_to="organizations/logo/", null=True, blank=True
    # )

    class Meta:
        """
        Metaclass for the Organization model
        """

        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]

    def __str__(self) -> str:
        """
        Returns:
            str: String representation of the organization.
        """
        return textwrap.wrap(self.name, 50)[0]
    
# class Hub(TimeStampedModel):
#     """
#     Stores information about a specific hub inside a :model:`organization.Organization`
#     Hubs are commonly known as terminals,hub.
#     """

#     id = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#     )
#     organization = models.ForeignKey(
#         Organization,
#         on_delete=models.CASCADE,
#         related_name="hubs",
#         verbose_name=_("Organization"),
#         help_text=_("The organization that the hub belongs to."),
#     )
#     name = models.CharField(
#         _("Hub Name"),
#         max_length=255,
#         unique=True,
#         help_text=_("The name of the hub."),
#     )
#     description = models.TextField(
#         _("Hub Description"),
#         max_length=255,
#         help_text=_("The description of the hub."),
#         blank=True,
#     )
#     address_line_1 = models.CharField(
#         _("Address Line 1"),
#         max_length=255,
#         help_text=_("The address line 1 of the hub."),
#     )
#     address_line_2 = models.CharField(
#         _("Address Line 2"),
#         max_length=255,
#         help_text=_("The address line 2 of the hub."),
#         blank=True,
#     )
#     location_cordinates= PointField(null=True,blank=True)
#     city = models.CharField(
#         _("City"),
#         max_length=255,
#         help_text=_("The city of the hub."),
    
    # state = USStateField(
    #     _("State"),
    #     blank=True,
    #     null=True,
    #     help_text=_("The state of the hub."),
    # )
    # zip_code = USZipCodeField(
    #     _("Zip Code"),
    #     blank=True,
    #     null=True,
    #     help_text=_("The zip code of the hub."),
    # )
    # phone_number = PhoneNumberField(
    #     _("Phone Number"),
    #     blank=True,
    #     null=True,
    #     help_text=_("The phone number of the hub."),
    # )
    # alternate_phone_number = PhoneNumberField(
    #     _("Alternate Phone Number"),
    #     blank=True,
    #     null=True,
    #     help_text=_("The alternate phone number of the hub."),
    # )
    # fax_number = PhoneNumberField(
    #     _("Fax Number"),
    #     blank=True,
    #     null=True,
    #     help_text=_("The fax number of the hub."),
    # )


    # class Meta:
    #     """
    #     Metaclass for the Hub model
    #     """

    #     verbose_name = _("Hub")
    #     verbose_name_plural = _("Hubs")
    #     ordering = ["name"]

    # def __str__(self) -> str:
    #     """Hub string representation.

    #     Returns:
    #         str: String representation of the HUB.
    #     """
    #     return textwrap.wrap(self.name, 50)[0]

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
    availability_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Vehicle(TimeStampedModel):
    active= models.BooleanField(default=True)

    no_plate = models.CharField(max_length=15, verbose_name="No Plate", unique=True)

    driver = models.ForeignKey(
        "Driver", related_name="drivers", on_delete=models.CASCADE
    )
    capacity = models.PositiveIntegerField()
    

    def __str__(self):
        return str(self.no_plate)


class RouteSettings(TimeStampedModel):
    class Utilization(models.TextChoices):
        
        minimum_vehicles = "Min_Veh", _(
            "Maximize Available Fleet   Capacity(Minimum Vehicle)"
        )  # Focuses more on capacity utilization,uses fewest vehicles which might travel longer distance


        Distance = "Min_Distance", _(
            "Balance Fleet Capacity  and Driving Time"
        )  # Finds a balance between distance and capacities available

        
        Manual = "MU", _("Manual Vehicle Selection")
    

    # class Mode(models.TextChoices):
    #     Distance = "Min_Distance", _("Minimize Distance")
    #     Arrival = "Ensure Arrival Time", _("Arrival Time")
    #     minimum_vehicles = "Min_Vehicles", _("Minimum Vehicle")
    class BranchChoices(models.TextChoices):

        Kilimani = "Kilimani", _(
            "Kilimani Hub"
        )  # Finds a balance between distance and capacities available

        ibuQA = "Rongai  ", _(
            "Rongai hub )"
        )  # Focuses more on capacity utilization,uses fewest vehicles which might travel longer distance

       

    selection = models.CharField(
        max_length=255,
        choices=Utilization.choices,
        default=Utilization.minimum_vehicles,
        verbose_name="Vehicle Selection",
    )

    # num_vehicles = models.PositiveIntegerField(
    #     default=6,
    # )
    # 
    # max_load_time=models.DurationField(blank=True, null=True)
    start_location=models.CharField(
        max_length=255,
        choices=BranchChoices.choices,
        default=BranchChoices.Kilimani,
        verbose_name="Start Location",
    )
    end_location=models.CharField(
        max_length=255,
        choices=BranchChoices.choices,
        default=BranchChoices.Kilimani,
        verbose_name="End Location",
    )
    start_address = PointField()
    end_address = PointField()
    departure_time = models.TimeField(blank=True, null=True)  # set departure tim
    finish_time = models.TimeField(blank=True, null=True)
    org=models.ForeignKey('Organization',null=True, on_delete=models.CASCADE)
    service_time=models.DurationField(blank=True, null=True)

    class Meta:
        verbose_name = _("RouteSettings")
        verbose_name_plural = _("RouteSettings")

    def __str__(self):
        return str(self.id)
    
    def save(self, **kwargs):
        if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["edited"]
        if self.finish_time and self.departure_time and self.finish_time < self.departure_time:
            raise ValidationError('Departure time can not be greater than finish time' )
        # if self.departure_time< now :
        #     raise ValidationError('Departure time can not be greater than finish time' )
            # self.code = generate_secret()
        # if self.p:
        #     raise Exception("Invalid transition.", self.status, allowed_next)


        super().save(**kwargs)


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
    delivery_adress = PointField()
    address = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
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
    earliest = models.DateTimeField(blank=True, null=True)
    latest = models.DateTimeField(blank=True, null=True)
    trip = models.ForeignKey(
        "Trip",
        related_name="deliveries_in_trip",
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
    
STATUS_DRAFT = "draft"
STATUS_PENDING = "pending"
STATUS_DISPATCHED = "dispatched"
STATUS_ONGOING = "ongoing"
STATUS_COMPLETED = "completed"

STATUS_CHOICE = (
        (STATUS_DRAFT, _("draft")),
        (STATUS_PENDING, _("pending")),
        (STATUS_DISPATCHED , _("dispatched")),
        (STATUS_ONGOING, _("ongoing")),
        (STATUS_COMPLETED, _("completed")),
        
    )
TRANSITIONS = {
   STATUS_DRAFT: [STATUS_PENDING,],
   STATUS_PENDING: [STATUS_DISPATCHED, STATUS_ONGOING],
   STATUS_DISPATCHED: [STATUS_ONGOING,STATUS_COMPLETED],
   STATUS_COMPLETED: [],
}


class Trip(TimeStampedModel):
    __current_status= None
   
    code = models.CharField(max_length=100, blank=True,editable=False)
    # driver = models.CharField(max_length=100, blank=True)
    distance = models.CharField(max_length=100, blank=True, null=True)
    load = models.CharField(max_length=100, blank=True)
    utilization = models.CharField(max_length=100, blank=True,editable=False)
    driver= models.ForeignKey(
        "Driver", related_name="driver_trips", null=True, on_delete=models.CASCADE
    )
    num_deliveries= models.CharField(max_length=100, blank=True,default=1,editable=False)
    departure_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    duration=models.DurationField(blank=True, null=True)
    fuel_consumption=models.PositiveIntegerField(blank=True, null=True)
    estimated_completion_time=models.DateTimeField(blank=True, null=True)
    completed_time= models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")
    
    
    
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
        
        
        return str(trip_deliveries)

    # duration=models.CharField(max_length=100, blank=True)

    # driver = models.ForeignKey(
    #     Driver,
    #     related_name='trips_assigned',
    #     blank=True,
    #     null=True,

    # )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__current_status = self.status

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        allowed_next = TRANSITIONS[self.__current_status]

        updated = self.status!= self.__current_status
        if self.pk and updated and self.status not in allowed_next:
            raise Exception("Invalid transition.", self.status, allowed_next)

        if self.pk and updated:
            self.__current_status= self.status
            
        if not self.code:
            self.code = set_trip_code()
        if not self.num_deliveries:
            self.num_deliveries = self.trip_deliveries

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def _transition(self, status):
        self.status= status
        self.save()

    def dispatch(self):
        from .tasks import send_sms_driver

        # we omit storing the driver on the model for simplicity of the example
        message = f"Dear {self.driver.name}, you have ben assigned trip {self.code} with {self.num_deliveries} deliveries  ."
        self._transition(STATUS_DISPATCHED)
        driver_phone = self.driver.phone
        send_sms_driver.delay(message,driver_phone)
        
    # def change_to_in_transit(self):
    #     # we omit storing the driver on the model for simplicity of the example
      
         
    #     self._transition(STATUS_DISPATCHED)
    #     message = f"Dear {self.driver.name}, you have ben assigned trip {self.code} with {self.num_deliveries} deliveries "
    #     phone=self.driver.phone
       
       
        
        

    # def save(self, **kwargs):
    #     if "update_fields" in kwargs and "last_modified" not in kwargs["update_fields"]:
    #         kwargs["update_fields"] = list(kwargs["update_fields"]) + ["edited"]
    #     if not self.code:
    #         self.code = generate_trip_secret()

    #     super().save(**kwargs)

    def __str__(self):
        return str(self.code)

   
