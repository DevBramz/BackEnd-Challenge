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
    dispatch_routes,
    plan_routes,
    
   
)

# order_router = DefaultRouter()
# order_router.register(r"orders", ViewSet, basename="orders")
delivery_router = DefaultRouter()


export_router = DefaultRouter()
optimize_router = DefaultRouter()
delivery_router.register("delivery", DeliveryViewSet, basename="delivery")

optimize_router.register("route", RouteViewSet, basename="route")


app_name = "core"
urlpatterns = [
    # path("", include(order_router.urls)),
    path("", include(delivery_router.urls)),
    path("", include(optimize_router.urls)),
  
    path("contact", Contact.as_view()),
    path("settings",  SettingsDetail.as_view(),name='settings'),
    path("plan", plan_routes,name='plan_routes'),
    path("dispatch", dispatch_routes),
    path('delis', views.index, name='delis'),
    # path('update/<int:todoId>/', views.update_settings, name='settings')
   
    # path("customer", views.Customer_Create.as_view(), name="customer"),
    # path("order", OrderListCreateAPIView.as_view(), name="order"),
   
]
