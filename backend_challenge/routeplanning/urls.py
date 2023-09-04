from django.urls import path

from .views import (
    RouteSettings,
    dispatch_routes,
    dispatch_single_route,
    order_route_settings_form,
    plan_order_route,
    plan_routes,
    post_order_route_sessions,
    view_order_route_summary,
    view_route_summary,
    view_single_route,
    view_single_route_summary,
)

app_name = "routeplanning"
urlpatterns = [
    # path("", include(package_router.urls)),
    path("configure/", RouteSettings.as_view(), name="route_settings"),
    path("plan", plan_routes, name="plan_routes"),
    path("routes-summary", view_route_summary, name="routes_summary"),
    path("single-route/<str:id>", view_single_route_summary, name="single_routes"),
    path("route/<str:id>", view_single_route, name="route_detail"),
    path("post_route_settings/", post_order_route_sessions, name="post_route_setting"),
    path("order_route_form/", order_route_settings_form, name="settings_route_form"),
    path("plan/order-route/", plan_order_route, name="plan_order_route"),
    path("order-route-summary/", view_order_route_summary, name="order_route_summary"),
    # path("add", ShipmentCreateView.as_view(), name="add_shipment"),
    # path("", include(delivery_router.urls)),
    # path("", include(optimize_router.urls)),
    # path("", include(trip_router.urls)),
    # path("contact", Contact.as_view()),
    # path("settings",  SettingsDetail.as_view(),name='settings'),
    # path("plan", plan_routes,name='plan_routes'),
    # path('trips', views.trips, name='trips'),
    path("dispatch", dispatch_routes),
    path("route/dispatch/<str:id>", dispatch_single_route, name="dispatch_route"),
    # path('delis', views.index, name='delis'),
    # path('route_summary',view_route_summary , name='route_summary'),
    # path('optimize-dispatch',optimize_dispatch , name='optimize_dispatch')
    # path('update/<int:todoId>/', views.update_settings, name='settings')
    # path("customer", views.Customer_Create.as_view(), name="customer"),
]
