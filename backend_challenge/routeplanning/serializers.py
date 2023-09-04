import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from locations.models import Location
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from tuma.common.serializers import GenericSerializer

from .models import RouteSettings

now = timezone.now()


class RouteSettingsSerializer(GenericSerializer):
    # routes_data = serializers.SerializerMethodField()
    start_point = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all().distinct("cords")
    )

    class Meta:
        model = RouteSettings
        extra_fields = [
            # "selection",
            "avoid_tolls",
            "avoid_highways",
        ]


class RoutesSettingForm(serializers.Serializer):
    start_point = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    service_time = serializers.IntegerField()
    # email = serializers.EmailField()
    # message = serializers.CharField()
    end_point = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    avoid_tolls = serializers.BooleanField(default=True)
    avoid_highways = serializers.BooleanField(default=True)
    finish_time = serializers.TimeField(
        allow_null=True,
        help_text="optional,",
    )
    depature_time = serializers.TimeField(initial=now)

    # def save(self):
    #     start_point = self.validated_data["start_point"]
    #     end_point = self.validated_data["end_point"]
    # send_email(from=email, message=message)
