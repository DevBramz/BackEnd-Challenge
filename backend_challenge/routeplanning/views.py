import json
import time
from datetime import datetime
from itertools import groupby

import dateutil.parser as dt
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.timezone import localtime
import googlemaps
from fleets.models import Driver, VehicleType
from locations.models import Location
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from routeplanning.order_route import ORPD
from routeplanning.pd import CVRPD
from routeplanning.route_end_anywhere import EAPD
from routeplanning.tasks import assign_driver_sms
from shipments.models import Shipment, ShipmentTask
from stops.models import Stop
from trips.models import OrderVehicle, Trip
from .models import RouteSettings
from .serializers import RouteSettingsSerializer
from django.views.decorators.cache import cache_page





def view_route_summary(request):
    return render(request, "route/route_summary.html")


def order_route_settings_form(request):
    return render(request, "route/order_route_settings.html")


def view_single_route_summary(request, *args, **kwargs):
    id = kwargs["id"]
    return render(request, "route/single_route_summary.html", {"id": id})


class RouteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for creating route settings and generating
    routes
    """

    queryset = RouteSettings.objects.all()
    serializer_class = RouteSettingsSerializer

    @action(
        detail=False,
        methods=["PUT"],
    )
    def post_settings(self, request):
        request = self.request
        user = self.request.user

        orguser = OrgUser.objects.get(user=user)

        data = request.data.get("settings", None)
        data2 = json.loads(data)

        settings = self.queryset.get(org_user=orguser)
        serializer = RouteSettingsSerializer(
            settings, data=data2, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # settings = self.queryset.filter(org_user=orguser).first()

        return Response(serializer.data)


@api_view(["POST"])
def post_order_route_sessions(request):
    order_settings_data = request.data.get("settings", None)
    print(order_route_settings_in_session)
    request.session["order_settings_data"] = order_settings_data
    return Response({"Success": "Order Route Settings Posted"})


@api_view(["POST"])
def post_route_settings_in_session(request):
    route_settings_data = request.data.get("route_settings", None)
    request.session["route_settings_data"] = route_settings_data
    return Response({"Success": "Route Settings Posted"})

  


def get_selected_shipments_in_session(request):
    selected_shipment_codes = request.session.get("selected_shipments")

    if selected_shipment_codes:
        codes_list = json.loads(selected_shipment_codes)
        shipments = Shipment.objects.filter(code__in=codes_list)
        return shipments
    raise CVRPException("selected shipments not found")


def get_selected_drivers_in_session(request):
    selected_driver_codes = request.session.get("selected_drivers")

    if selected_driver_codes:
        codes_list = json.loads(selected_driver_codes)
        drivers = Driver.objects.filter(code__in=codes_list)
        return drivers
    raise CVRPException("selected drivers not found")


def order_route_settings_in_session(request):
    selected_vehicle = request.session.get("selected_vehicle")

    if selected_vehicle:
        return selected_vehicle
    raise CVRPException("selected vehicle not found")







@api_view()
def plan_routes(request):
    user = request.user
    orguser = OrgUser.objects.get(user=user)
    settings = orguser.routesettings
    # settings_data = RouteSettingsSerializer(settings).data
    start_address = settings.start_point.address
    start_latlong = settings.start_point.latlong
    start_cords = settings.start_point.cords
    departure_time = localtime(settings.departure_time)

    shipments = get_selected_shipments_in_session(request)
    if not shipments:
        raise DispatchException

    drivers = get_selected_drivers_in_session(request)
    if not drivers:
        raise DispatchException

    route = CVRPD(
        drivers, shipments, start_address, start_latlong, start_cords, departure_time
    )  # Rout

    routes_summary = route.generate_routes()

    trip_data = routes_summary.get("routes", None)


    request.session["trip_data"] = trip_data
    return Response(routes_summary)


def view_order_route_summary(request):
    return render(request, "route/order_route.html")


@api_view()
def view_single_route(request, *args, **kwargs):
    routes = request.session.get("trip_data", None)
    index = int(kwargs["id"]) - 1
    route = routes[index]
    stop_data = route["stop_data"]
    route_stops = []
    for stop in stop_data:
        address = stop["stop_address"]
        lat = stop["stop_latlong"][0]
        long = stop["stop_latlong"][1]
        dict = {"lat": lat, "lng": long}
        route_stop = [dict, address]
        route_stops.append(route_stop)
    route_stops[1:]  # removes the start point

    return Response(route_stops)




@api_view()
def dispatch_single_route(request, *args, **kwargs):
    org = request.user.organization
    routes = request.session.get("trip_data", None)

    index = int(kwargs["id"]) - 1
    route = routes[index]
    if route:
        driver_name = route["driver_name"]
        driver = Driver.objects.get(displayName=driver_name)
        num_stops = route["num_stops"]
        shipments = route["route_shipments"]
        route_shipments = json.loads(shipments)
        shipment_ids = [i["id"] for i in route_shipments]
        shipments_in_trip = Shipment.objects.filter(id__in=list(shipment_ids))

        distance = route["distance"]
        duration_seconds = route["duration"]
        duration = time.strftime("%Hhrs:%Mmins", time.gmtime(duration_seconds))

        departure_time = route["departure_time"]
        departure = datetime.strptime(departure_time, "%a %d %b %Y, %I:%M%p")
        stop_info = route["stop_data"]

        load = route["load"]
        estimated_completion_time = route["est"]
        est = datetime.strptime(estimated_completion_time, "%a %d %b %Y, %I:%M%p")

        trip = Trip.objects.create(
            load=load,
            duration=duration,
            distance=distance,
            driver=driver,
            num_stops=num_stops,
            departure_time=departure,
            estimated_completion_time=est,
            organization=org,
            status="assigned",
        )
        sequence = 0
        for stop in stop_info:
            stop_eta = stop["stop_eta"]
            eta = datetime.strptime(stop_eta, "%a %d %b %Y, %I:%M%p")
            address = stop.get("stop_address", None)

            location = Location.objects.get(address=address)
            stop = Stop.objects.create(
                organization=org,
                eta=eta,
                sequence=sequence,
                location=location,
                trip=trip,
            )
            ShipmentTask.objects.filter(
                Q(location=stop.location) & Q(shipment__in=list(shipments_in_trip))
            ).update(stop=stop)
            sequence += 1

            # [stop.stop_tasks.add(task)for task in tasks_in_stop]

        for shipment in shipments_in_trip:
            shipment.trip = trip
            shipment.status = "assigned"
            shipment.save()
        trip_url = reverse("trips:trip_stops", args=(trip.pk,), request=request)
     
      
        del route
        # del request.session["selected_shipments"]
        # del request.session["selected_drivers"]
        return Response({"Success": "Route Dispatched to Driver"})
    return Response(
        {"Failed": "Dispatch cannot occur, No route data found"},
        status=status.HTTP_400_BAD_REQUEST,
    )

    # trip.dispatch()
    #   send sms  post save signal5

    # shipments_in_route=Shipment,objects.filter(id__in)


@api_view()
def dispatch_routes(request):
    org = request.user.organization
    """
    Creates and dispatches trip from routes
    """
    routes = request.session.get("trip_data", None)

    if routes:
        with transaction.atomic():
            for i, route in enumerate(routes):
                driver = route["driver_name"]
                driver = Driver.objects.get(displayName=driver)
                num_stops = route["num_stops"]
                shipments = route["route_shipments"]
                route_shipments = json.loads(shipments)
                shipment_ids = [i["id"] for i in route_shipments]
                shipments_in_trip = Shipment.objects.filter(id__in=shipment_ids)
                distance = int((route["distance"] / 1000))
                duration_seconds = route["duration"]
                minutes, seconds = divmod(duration_seconds, 60)
                hours, minutes = divmod(minutes, 60)
                duration = "%d:%02d:%02d" % (hours, minutes, seconds)

                departure_time = route["departure_time"]
                departure = datetime.strptime(departure_time, "%a %d %b %Y, %I:%M%p")
                stop_info = route["stop_data"]

                load = route["load"]
                estimated_completion_time = route["est"]
                est = datetime.strptime(
                    estimated_completion_time, "%a %d %b %Y, %I:%M%p"
                )

                # vehicle_utilization = route["vehicle_capacity_utilization"]
                # utilization = str(vehicle_utilization)
                # distance = route["distance"]
                # tasks = route["deliveries"]
                # deliverys = Delivery.objects.filter(code__in=tasks)
                # num_deliveries = str(deliverys.count())

                trip = Trip.objects.create(
                    load=load,
                    duration=duration,
                    distance=distance,
                    driver=driver,
                    num_stops=num_stops,
                    departure_time=departure,
                    estimated_completion_time=est,
                    organization=org,
                    status="assigned"
                    # depature_time=datetime.datetime.now
                )
                sequence = 0
                for stop in stop_info:
                    stop_eta = stop["stop_eta"]

                    eta = datetime.strptime(stop_eta, "%a %d %b %Y, %I:%M%p")
                    address = stop.get("stop_address", None)

                    location = Location.objects.get(address=address)
                    stop = Stop.objects.create(
                        organization=org,
                        eta=eta,
                        sequence=sequence,
                        location=location,
                        trip=trip,
                    )
                    ShipmentTask.objects.filter(
                        Q(location=stop.location)
                        & Q(shipment__in=list(shipments_in_trip))
                    ).update(stop=stop)
                    sequence += 1

                # trip.dispatch()
                #   send sms  post save signal5

                # shipments_in_route=Shipment,objects.filter(id__in)

                for shipment in shipments_in_trip:
                    shipment.trip = trip
                    shipment.status = "assigned"
                    shipment.save()

                trip_url = reverse("trips:trip_stops", args=(trip.pk,), request=request)
                # print(assigned_trip)
                m = f"hello ,{driver.displayName} You have a new trip request.Click here to view {trip_url}"

                # stop_sequences = route["stop_sequences"]
                #  route["distance"]
                # trip.deliveries_in_trip.add(delivery)
                # send_sms_recepient(delivery.id)
            # transaction.on_commit(lambda: send_sms_recepient.delay(delivery.id))

            # print(trip.deliveries_in_trip.all())

            # del request.session["trip_data"][index]
            # del request.session["selected_shipments"]
            del request.session["selected_drivers"]
            return Response({"message": "Trip_created"})
    return Response(
        {"message": "Dispatch cannot occur, No route data found"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view()
def dispatch_order_route(request):
    org = request.user.organization
    """
    Creates and dispatches trip from routes
    """
    routes = request.session.get("trip_data", None)

    if routes:
        with transaction.atomic():
            for i, route in enumerate(routes):
                # driver = route["driver_name"]
                # driver = Driver.objects.get(displayName=driver)

                num_stops = route["num_stops"]
                shipments = route["route_shipments"]
                route_shipments = json.loads(shipments)
                shipment_ids = [i["id"] for i in route_shipments]
                shipments_in_trip = Shipment.objects.filter(id__in=list(shipment_ids))

                distance = route["distance"]
                duration_seconds = route["duration"]
                duration = time.strftime("%Hhrs:%Mmins", time.gmtime(duration_seconds))

                departure_time = route["departure_time"]
                departure = datetime.strptime(departure_time, "%a %d %b %Y, %I:%M%p")
                stop_info = route["stop_data"]

                load = route["load"]
                estimated_completion_time = route["est"]
                est = datetime.strptime(
                    estimated_completion_time, "%a %d %b %Y, %I:%M%p"
                )

                trip = Trip.objects.create(
                    load=load,
                    duration=duration,
                    distance=distance,
                    num_stops=num_stops,
                    departure_time=departure,
                    estimated_completion_time=est,
                    organization=org,
                    status="Awaiting_Assignment",
                )
                sequence = 0
                for stop in stop_info:
                    stop_eta = stop["stop_eta"]
                    eta = datetime.strptime(stop_eta, "%a %d %b %Y, %I:%M%p")
                    address = stop.get("stop_address", None)

                    location = Location.objects.get(address=address)
                    stop = Stop.objects.create(
                        organization=org,
                        eta=eta,
                        sequence=sequence,
                        location=location,
                        trip=trip,
                    )
                    ShipmentTask.objects.filter(
                        Q(location=stop.location)
                        & Q(shipment__in=list(shipments_in_trip))
                    ).update(stop=stop)
                    sequence += 1

                    # [stop.stop_tasks.add(task)for task in tasks_in_stop]

                for shipment in shipments_in_trip:
                    shipment.trip = trip
                    # shipment.status = "assigned"
                    shipment.save()

                trip_url = reverse("trips:trip_stops", args=(trip.pk,), request=request)

                # trip.dispatch()
                #   send sms  post save signal5

                trip_url = reverse("trips:trip_stops", args=(trip.pk,), request=request)
                # print(assigned_trip)
                m = f"hello ,{driver.displayName} You have a new trip request.Click here to view {trip_url}"

                # stop_sequences = route["stop_sequences"]
                #  route["distance"]
                # trip.deliveries_in_trip.add(delivery)
                # send_sms_recepient(delivery.id)
            # transaction.on_commit(lambda: send_sms_recepient.delay(delivery.id))

            # print(trip.deliveries_in_trip.all())

            # del request.session["trip_data"][index]
            # del request.session["selected_shipments"]
            del request.session["selected_drivers"]
            return Response({"message": "Trip_created"})
    return Response(
        {"message": "Dispatch cannot occur, No route data found"},
        status=status.HTTP_400_BAD_REQUEST,
    )





class RouteSettings(APIView):
    queryset = RouteSettings.objects.all()
    template_name = "route/route_settings.html"

    serializer_class = RouteSettingsSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def get_queryset(self):
        """Filter the queryset to only include the current user's organization

        Returns:

        """
        organization = self.request.user.organization

        return self.queryset.filter(  # type: ignore
            organization=organization  # type: ignore
        ).all()

    # def get_object(self, pk):
    #     try:
    #         return self.queryset.get(pk=pk)
    #     except RouteSettings.DoesNotExist:
    #         raise Http404

    def get(
        self,
        request,
    ):
        settings = self.queryset.first()
        serializer = RouteSettingsSerializer(settings)
        return Response({"serializer": serializer, "settings": settings})

    def post(self, request):
        user = self.request.user
       

        settings = self.queryset.get(org_user=orguser)
        serializer = RouteSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response({"serializer": serializer, "settings": settings})



