import asyncio
import json
import logging
import time
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync, sync_to_async
from common.views import OrganizationMixin
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View
from redis import ConnectionError, Redis, RedisError
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from trips.models import Trip
from trips.serializers import TripSerializer
from trips.tasks import send_dispatch_sms

logger = logging.getLogger(__name__)

# from shipments.tasks import send_dispatch_sms

try:
    if settings.REDIS_URL:
        r = Redis.from_url(url=settings.REDIS_URL, decode_responses=True)
    else:
        r = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
except RedisError:
    logger.error(
        f"Redis failed connection to {settings.REDIS_HOST}:{settings.REDIS_PORT}."
    )


# r = redis.Redis(host="localhost", port=6379, decode_responses=True)


@login_required
def all_trips(request):
    """
    A simple ViewSet for viewing and editing the accounts
    associated with the user.
    """
    return render(request, "trips/trips_table.html")


@login_required
def view_stops_detail(request, id):
    """
    A simple ViewSet for driver viewing
    associated with the user.
    """
    trip = get_object_or_404(Trip, id=id)
    stops = trip.stops.all()
    d = {
        "trip": trip,
        "stops": stops,
    }

    return render(request, "trips/trip.html", d)


@login_required
def track_trip(request, code):
    """
    A simple ViewSet for driver viewing
    associated with the user.
    """
    trip = get_object_or_404(Trip, code=code)
    stops = trip.stops.all()
    d = {
        "trip": trip,
        "stops": stops,
    }

    return render(request, "trips/triptracking.html", d)


@login_required
def view_trip_summary(request, id):
    """
    A simple ViewSet for driver viewing
    associated with the user.
    """
    trip = get_object_or_404(Trip, id=id)
    stops = trip.stops.all()
    d = {
        "trip": trip,
        "stops": stops,
    }
    return render(request, "trips/trip_stops.html", d)


# class TripStopDetail(View):
#     template_name = "trips/trip_stops.html"

#     def get(self, request, id=id):


class TripDriver(View):
    """
    A simple View for driver viewing the trip in detail
    after starting to be rewritten

    """

    template_name = "trips/trip_driver_view.html"

    def get(self, request, code=None):
        trip = get_object_or_404(Trip, code=code)
        stops = trip.stops.all()

        first_stop = trip.stops.first()
        last = trip.stops.last()
        if first_stop.location == last.location:
            last.stop_tasks.filter(task_type="PickUp").update(stop=first_stop)

        d = {
            "trip": trip,
            "stops": stops,
        }

        return render(request, self.template_name, d)


class TripViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing the accounts
    associated with the user.
    """

    serializer_class = TripSerializer
    queryset = Trip.objects.all()
    lookup_field = "code"

    @action(detail=True, methods=["trip"], permission_classes=[])
    def start_trip(self, request, **kwargs):
        """Update the trip from start to ongoing ."""
        trip = self.get_object()
        trip.status = "ongoing"
        trip.save()
        shipments_in_trip = trip.shipments.all()

        for shipment in shipments_in_trip:
            shipment.status = "dispatched"
            shipment.save()

            transaction.on_commit(
                lambda: send_dispatch_sms(shipment.id),
            )
            # send sms to shipment recepient and an email to shipment sender

        return self.retrieve(request, [], **kwargs)

    @action(detail=True, methods=["GET"], permission_classes=[])
    def view_trip_stops(self, request, **kwargs):
        """Update the trip from start to ongoing ."""
        trip = self.get_object()

        trip.stops.all()
        # send sms to shipment recepient and an email to shipment sender

        return self.retrieve(request, [], **kwargs)


@api_view(["POST"])
def accept_start_trip(request):
    data = request.data
    code = data.get("trip_code", None)
    pos = data.get("location", None)

    r.hset(code, mapping=pos)
    # now = timezone.now()
    trip = get_object_or_404(Trip, code=code)
    trip.status = "ongoing"
    # trip.actual_departure_time = now
    trip.save()

    # time_difference = (trip.actual_departure_time - trip.departure_time).total_seconds()

    # trip.stops.all().update(eta=F("eta") + timedelta(seconds=time_difference))
    # shipments_in_trip = trip.shipments.all()

    # for shipment in shipments_in_trip:
    #     shipment.status = "Out for Delivery"
    #     shipment.save()
    #     tracking_url = reverse(
    #         "tracking:track_shipment", args=(shipment.tracking_id,), request=request
    #     )

    #     send_dispatch_sms(shipment.id)
    # asyncio.run(mesage)

    # print(mesage)

    response = {"msg": "Trip Started"}
    return Response(response, status=200)


@api_view(["GET"])
def trip_route(request, *args, **kwargs):
    code = kwargs["code"]
    trip = Trip.objects.get(code=code)
    if trip:
        stops = trip.stops.select_related("location").all()
        route_stops = []
        for stop in stops:
            location = stop.location
            address = location.address
            lat = location.cords.y
            lng = location.cords.x
            dict = {"lat": lat, "lng": lng}  # change to google maps latlong format
            route_stop = [dict, address]
            route_stops.append(route_stop)
        return Response(route_stops)
    else:
        response = {"msg": "No routes found in trip"}
        return Response(response, status=404)


@api_view(["post"])
def post_vehicle_location(request):
    data = request.data
    key = data.get("key", None)
    pos = data.get("location", None)
    print(type(pos))

    # data={time:time.time(), pos:pos}

    r.hset(key, mapping=pos)
    return Response(201)


@api_view(["get"])
def get_vehicle_location(request, *args, **kwargs):
    code = kwargs["code"]

    vehicle_location = r.hgetall(code)

    latitude = vehicle_location.get("lat", None)
    if latitude:
        lat = float(latitude)

    longitude = vehicle_location.get("lng", None)
    if longitude:
        lng = float(longitude)

    driver_location = {"lat": lat, "lng": lng}
    if driver_location:
        response = driver_location
        return Response(response)
    else:
        response = {"msg": "Driver location  not assigned"}
        return Response(response, status=400)

    # if request.method == "GET":
    #     items = {}
    #     count = 0
    #     for key in redis_instance.keys("*"):
    #         items[key.decode("utf-8")] = redis_instance.get(key)
    #         count += 1
    #     response = {"count": count, "msg": f"Found {count} items.", "items": items}
    #     return Response(response, status=200)
    # elif request.method == "trip":
    #     item = json.loads(request.body)
    #     key = list(item.keys())[0]
    #     value = item[key]
    #     redis_instance.set(key, value)
    #     response = {"msg": f"{key} successfully set to {value}"}
    #     return Response(response, 201)


# @api_view(["GET", "PUT", "DELETE"])
# def manage_item(request, *args, **kwargs):
#     if request.method == "GET":
#         if kwargs["key"]:
#             value = redis_instance.get(kwargs["key"])
#             if value:
#                 response = {"key": kwargs["key"], "value": value, "msg": "success"}
#                 return Response(response, status=200)
#             else:
#                 response = {"key": kwargs["key"], "value": None, "msg": "Not found"}
#                 return Response(response, status=404)
#     elif request.method == "PUT":
#         if kwargs["key"]:
#             request_data = json.loads(request.body)
#             new_value = request_data["new_value"]
#             value = redis_instance.get(kwargs["key"])
#             if value:
#                 redis_instance.set(kwargs["key"], new_value)
#                 response = {
#                     "key": kwargs["key"],
#                     "value": value,
#                     "msg": f"Successfully updated {kwargs['key']}",
#                 }
#                 return Response(response, status=200)
#             else:
#                 response = {"key": kwargs["key"], "value": None, "msg": "Not found"}
#                 return Response(response, status=404)

#     elif request.method == "DELETE":
#         if kwargs["key"]:
#             result = redis_instance.delete(kwargs["key"])
#             if result == 1:
#                 response = {"msg": f"{kwargs['key']} successfully deleted"}
#                 return Response(response, status=404)
#             else:
#                 response = {"key": kwargs["key"], "value": None, "msg": "Not found"}
#                 return Response(response, status=404)
