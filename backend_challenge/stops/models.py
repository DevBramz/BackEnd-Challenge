from django.db import models
from django.utils.translation import gettext_lazy as _
from locations.models import Location
from trips.models import Trip

from tuma.common.models import GenericModel


class Stop(GenericModel):
    """
    Stores information related to a shipment Stop`.

    """

    class StopStatus(models.TextChoices):
        PENDING = "P", _("Pending")
        IN_PROGRESS = "IP", _("In Progress")
        ARRIVED = "AR", _("Arrived")
        EN_ROUTE = "EN", _("En Route")
        CANCELLED = "CL", _("Cancel")
        LEFT = "L", _("Left")
        # VISITED="V", _("Visited")

    stop_status = models.CharField(
        max_length=2, choices=StopStatus.choices, default=StopStatus.PENDING
    )

    sequence = models.PositiveIntegerField(
        _("Sequence"),
        default=1,
        help_text=_("The sequence of the stop in the trip."),
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stops",
        verbose_name=_("trip"),
        help_text=_("The trip that the stop belongs to."),
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="stops",
        related_query_name="stop",
        verbose_name=_("Location"),
        help_text=_("The location of the stop."),
    )

    eta = models.DateTimeField(
        _("Stop ETA "),
        help_text=_("The time the vehicle is expected to arrive at the stop."),
        null=True,
        blank=True,
    )
    arrival_time = models.DateTimeField(
        _("Stop Arrival Time"),
        null=True,
        blank=True,
        help_text=_("The time the vehicle actually arrived at the stop."),
    )
    departure_time = models.DateTimeField(
        _("Stop Departure Time"),
        null=True,
        blank=True,
        help_text=_("The time the vehicle actually departed from the stop."),
    )

    #     shipment_tasks=models.ArrayField(models.CharField(max_length=512,help_text=_("List of shipments tasks ."),)if all the tasks in a stop are completed, the stop becomes complete but if they are not completed the stop become
    #    )
    # stop_type = ChoiceField(
    #     choices=StopChoices.choices,
    #     help_text=_("The type of stop."),
    # )

    def __str__(self):
        return self.location.address

    @property
    def tasks_in_stop(self):
        return self.stop_tasks.all()

    class Meta:
        """
        Metaclass for the Stop model
        """

        verbose_name = "Stop"
        verbose_name_plural = _("Stops")


# Create your models here.
