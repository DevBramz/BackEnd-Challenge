import datetime

from django.contrib.gis.geos import Point
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _





# Create your models here.
class RouteSettings(GenericModel):
    class StartOptions(models.TextChoices):
        Branch/Depot = "BR", _("Select from Locations/Branches")
        DriverAdress = "DA", _("Driver Current Address")

    start_options = models.CharField(
        max_length=255,
        choices=StartOptions.choices,
        default=StartOptions.Favorite,
        verbose_name="Start Options",
    )
    # start_options=models.

    start_point = models.ForeignKey(
        Location,
        verbose_name=_("start point"),
        on_delete=models.CASCADE,
        help_text=_("Route Origin"),
    )
    # return_route = models.BooleanField(default=False)

    end_point = models.ForeignKey(
        Location,
        verbose_name=_("end point"),
        on_delete=models.CASCADE,
        help_text=_("optional,Select the endpoint of your route"),
        related_name="route_end",
        blank=True,
        null=True,
    )
    departure_time = models.DateTimeField(
        help_text=_(
            "set future time, defaults to now, for eta  calculation and route optimization purposes"
        ),
    )  # set departure tim
    finish_time = models.DateTimeField(blank=True, null=True, help_text=_("optional,"))
    service_time = models.PositiveIntegerField(
        verbose_name=_("Service time(mins)"),
        help_text=_("average time taken to complete a task"),
    )
    avoid_tolls = models.BooleanField(default=True)
    avoid_highways = models.BooleanField(default=True)
   
    class Meta:
        verbose_name = _("RouteSettings")
        verbose_name_plural = _("RouteSettings")

    def __str__(self):
        return str(self.id)
