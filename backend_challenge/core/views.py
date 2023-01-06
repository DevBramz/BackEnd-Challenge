import csv
from django.http import HttpResponse
from rest_framework import status, viewsets, filters
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import api_view, permission_classes
from .models import Customer, Delivery, Order, RouteSettings
from .serializers import (
    CustomerSerializer,
    OrderSerializer,
    RouteSettingsSerializer,
    DeliverySerializer,
)
from .tasks import send_sms
from .exporter import ExportViewMixin
from django.template.defaultfilters import slugify
from rest_framework.reverse import reverse
from django.shortcuts import redirect

# from .tsm import main


class CustomerProfileException(NotFound):
    """Exception raised when customer profile  is not present in the data."""

    status_code = 404
    default_detail = "Customer Profile not found.Create Cussomer profile"


class Customer_Create(APIView):
    permission_classes = [IsAuthenticated]

    """
   create a new customer
    """

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.


class OrderListCreateAPIView(ListCreateAPIView):

    """"""

    model = Order
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):

        user = self.request.user
        try:
            customer = Customer.objects.get(user=user)
        # if not customer:
        #     raise Http404("Create Customer Profile")
        except ObjectDoesNotExist as snip_no_exist:
            raise CustomerProfileException() from snip_no_exist
        return self.queryset.filter(customer=customer)

    def perform_create(self, serializer):
        if serializer.is_valid():
            order = serializer.save()
            transaction.on_commit(lambda: send_sms(order.id))


class OrderViewSet(
    viewsets.ModelViewSet,
    ExportViewMixin,
):
    """
    A viewset that provides the standard actions
    """

    model = Order
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["code", "category", "status"]

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context.update({"request": self.request})
    #     return context

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Order.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
            print(queryset)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
            print(queryset)

        return queryset

    @action(detail=True)
    def clone_order(self, request, pk=None):
        """
        Method to clone an order
        """
        order = self.get_object()
        order.pk = None
        order._state.adding = True

        cloned = order.save()

        if cloned:
            data = {"order_id": cloned.id, "order_code": clone.code}
            return Response(data)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def export_orders(self, request, *args, **kwargs):
        """
        Method to export orders
        """
        queryset = self.get_queryset()
        print(queryset)

        return self.export(queryset)


class ExportOrdersView(APIView, ExportViewMixin):
    """
    Viewset to export order
    """

    model = Order
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["code", "category", "status"]
    renderer_classes = [TemplateHTMLRenderer]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Order.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
            print(queryset)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
            print(queryset)

        return queryset

    def get_serializer(self, queryset, many=True):
        return self.serializer_class(
            queryset,
            many=many,
        )

    def get(self, request, format=None):
        orders = self.get_queryset()
        return Response({"orders": orders}, template_name="orders.html")

    # def export(self,request, *args, **kwargs):
    #     response = HttpResponse(content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename="export.csv"'

    #     # serializer = self.get_serializer(
    #     #         Order.objects.all(),
    #     #         many=True
    #     #     )
    #     # qs=Order.objects.all()
    #     # category = self.request.query_params.get('category')
    #     # if category is not None:
    #     #     qs = qs.filter(category=category)

    #     model=Order
    #     resp = HttpResponse(content_type="text/csv")
    #     resp["Content-Disposition"] = "attachment; filename=%s.csv" % (
    #         slugify(model.__name__)
    #     )
    #     writer = csv.writer(resp)
    #     # Write headers to CSV file
    #     headers = [
    #         "code",
    #         "category",
    #     ]
    #     # opts = queryset.model._meta
    #     # field_names = [field.name for field in opts.fields]

    #     for field in model._meta.fields:
    #         if field.name not in ("added", "edited", "id", "code", "category"):
    #             headers.append(field.name)

    #     writer.writerow(headers)
    #     # Write data to CSV file
    #     for obj in self.get_queryset():
    #         row = []
    #         for field in headers:
    #             if field in headers:
    #                 val = getattr(obj, field)
    #                 if callable(val):
    #                     val = val()
    #                 row.append(val)
    #         writer.writerow(row)
    #     # Return CSV file to browser as download
    #     if resp:

    #         return resp
    #     else:
    #         return Response(
    #             {"status": "failed", "message": "export failed"},
    #             status=status.HTTP_410_GONE,
    # )


# Routes API is the next generation, performance optimized version of the existing Directions API and Distance Matrix API. It helps you find the ideal route from A to Z, calculates ETAs and distances for matrices of origin and destination locations, and also offers new features.
#     if mode not in ["driving", "walking", "bicycling", "transit"]:
#             raise ValueError("Invalid travel mode.")
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def routing_view(request, format=None):
#     content = {
#         "routes":,  # `django.contrib.auth.User` instance.
#     }

#     return Response(content)
class DeliveryViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    @action(detail=True)
    def clone_order(self, request, pk=None):
        """
        Method to clone an order
        """
        delivery = self.get_object()
        delivery.pk = None
        delivery._state.adding = True

        delivery.save()

        if delivery:
            data = {"order_id": delivery.id, "order_code": delivery.code,"url":reverse('core:delivery-detail', args=[pk], request=request)}
            return Response(data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    queryset = RouteSettings.objects.all()
    serializer_class = RouteSettingsSerializer
    

    

    
    

