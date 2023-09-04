from django.conf import settings
from django.urls import include, path
from trips.views import (  # manage_item,
    TripDriver,
    accept_start_trip,
    all_trips,
    get_vehicle_location,
    post_vehicle_location,
    track_trip,
    trip_route,
    view_trip_summary,
)

app_name = "trips"
urlpatterns = [
    # path("", include(package_router.urls)),
    path("all-trips", all_trips, name="all_trips"),
    path("accept-start-trip", accept_start_trip, name="accept_start_trip"),
    path("stops/<int:id>", view_trip_summary, name="trip_stops"),
    path("route/<str:code>", trip_route, name="trip_route"),
    path(
        "driver/ongoing/<str:code>", TripDriver.as_view(), name="ongoing_trip"
    ),  # To be rewritten
    # path('', manage_items, name="items"),
    # path("<slug:key>", manage_item, name="single_item"),
    path("post/vehicle/location", post_vehicle_location, name="post_vehicle_location"),
    path("get/vehicle/location/<str:code>", get_vehicle_location, name="track_vehicle"),
    path("track/trip/<str:code>", track_trip, name="track_trip"),
]
