from rest_framework import status, viewsets, filters
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .tasks import send_sms
from .exporter import ExportViewMixin


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


class OrderViewSet(viewsets.ModelViewSet,ExportViewMixin,):
    """
    A viewset that provides the standard actions
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["code", "category", "status"]

    @action(detail=True)
    def clone_order(self, request, pk=None):
        """
        Method to clone an order
        """
        order = self.get_object()
        order.pk = None

        order.save()

        if order:
            return Response({"status": "order created from clone"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def export_orders(self, request, *args, **kwargs):
        """
        Method to export orders
        """
        queryset = self.queryset
        print(queryset)
        return self.export(queryset)
        
    
   