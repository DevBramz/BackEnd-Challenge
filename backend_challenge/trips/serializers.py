from django.utils import timezone
from rest_framework import serializers
from stops.serializers import StopSerializer

from tuma.common.serializers import GenericSerializer

from .models import Trip

now = timezone.now()


class TripSerializer(GenericSerializer):
    driver = serializers.StringRelatedField()
    stops = StopSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        extra_fields = [
            "driver",
            "stops",
            # "selection",
        ]
