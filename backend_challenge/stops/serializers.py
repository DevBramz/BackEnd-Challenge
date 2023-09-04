from rest_framework import serializers

from tuma.common.serializers import GenericSerializer

from .models import Stop


class StopSerializer(GenericSerializer):
    class Meta:
        model = Stop
        extra_fields = []
