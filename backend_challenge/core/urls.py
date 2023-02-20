from django.urls import include, path
from rest_framework.routers import DefaultRouter


from . import views
from .views import (
    # OrderListCreateAPIView,
    # OrderViewSet,
    # ExportOrdersView,
    DeliveryViewSet,
    RouteViewSet,
    Contact,
    SettingsDetail,
    TripViewSet,
    dispatch_routes,
    plan_routes,
    view_route_summary,
    optimize_dispatch
    
   
)

# order_router = DefaultRouter()
# order_router.register(r"orders", ViewSet, basename="orders")
delivery_router = DefaultRouter()


export_router = DefaultRouter()
optimize_router = DefaultRouter()
trip_router=DefaultRouter()
delivery_router.register("delivery", DeliveryViewSet, basename="delivery")
trip_router.register("trip", TripViewSet, basename="trip")

optimize_router.register("route", RouteViewSet, basename="route")


app_name = "core"
urlpatterns = [
    # path("", include(order_router.urls)),
    path("", include(delivery_router.urls)),
    path("", include(optimize_router.urls)),
    path("", include(trip_router.urls)),
  
    path("contact", Contact.as_view()),
    path("settings",  SettingsDetail.as_view(),name='settings'),
    path("plan", plan_routes,name='plan_routes'),
    path('trips', views.trips, name='trips'),
    path("dispatch", dispatch_routes),
    path('delis', views.index, name='delis'),
   
    path('route_summary',view_route_summary , name='route_summary'),
    path('optimize-dispatch',optimize_dispatch , name='optimize_dispatch')
    # path('update/<int:todoId>/', views.update_settings, name='settings')
   
    # path("customer", views.Customer_Create.as_view(), name="customer"),
    
   
]
