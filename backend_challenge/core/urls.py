from django.urls import include, path
from rest_framework.routers import DefaultRouter




from . import views
from .views import OrderListCreateAPIView,OrderViewSet

router = DefaultRouter()
router.register(r'orders',  OrderViewSet)

app_name = "core"
urlpatterns = [
    path("", include(router.urls)),
    path("customer", views.Customer_Create.as_view(), name="customer"),
    path("order", OrderListCreateAPIView.as_view(), name="order"),
    
]
