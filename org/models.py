import textwrap
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

# from backend_challenge.core.modelsODE import TimeStampedModel

# Create your models here.


class Organization(models.Model):
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

    org_type = models.CharField(
        max_length=10,
        choices=OrganizationTypes.choices,
        default=OrganizationTypes.ASSET,
        verbose_name=_("Organization Type"),
        help_text=_("The type of organization."),
    )

    # )
    currency = models.CharField(
        _("Currency"),
        max_length=255,
        default="USD",
        help_text=_("The currency that the organization uses"),
    )
    # trip = models.ForeignKey(
    #     "Trip",
    #     related_name="deliveries_in_trip",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )
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
