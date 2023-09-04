from common.views import OrganizationMixin
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import Stop
from .serializers import StopSerializer

# Create your views herefrom rest_framework import viewsets


# def create_delivery(request):
#     return render(request, "shipments/create_delivery.html")


# def create_shipment(request):
#     return render(request, "shipments/create_shipment.html")


# Thanks for registering! Here's your activation link:
# {{ request.scheme }}://{{ request.get_host }}{% url 'registration_activate' activation_key %}

# Returns the absolute URI form of location. If no location is provided, the location will be set to request.get_full_path().

# If the location is already an absolute URI, it will not be altered. Otherwise the absolute URI is built using the server variables available in this request. For example:

# >>> request.build_absolute_uri()
# 'https://example.com/music/bands/the_beatles/?print=true'
# >>> request.build_absolute_uri('/bands/')
# 'https://example.com/bands/'
# >>> request.build_absolute_uri('https:/


# def all_trips(request):
#     """
#     A simple ViewSet for viewing and editing the accounts
#     associated with the user.
#     """
#     return render(request, "trips/trips_table.html")


class StopViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing the accounts
    associated with the user.
    """

    serializer_class = StopSerializer
    queryset = Stop.objects.all()
    # lookup_field = "code"


# Create your views here.
