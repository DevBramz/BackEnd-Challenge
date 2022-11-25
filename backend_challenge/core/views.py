import json

import requests
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer,CustomerProfileUnavailable
from .tasks import send_sms
from django.db import transaction
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException, NotFound, ValidationError

class CustomerProfileException(NotFound):
    """Exception raised when customer profile  is not present in the data."""
    status_code = 404
    default_detail = 'Customer Profile not found.Create Cussomer profile'



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
    
        user= self.request.user
        try:
            customer= Customer.objects.get(user=user)
        # if not customer:
        #     raise Http404("Create Customer Profile")
        except ObjectDoesNotExist as snip_no_exist:
            raise CustomerProfileException() from snip_no_exist
        return self.queryset.filter(customer=customer)

    def perform_create(self, serializer):
        if serializer.is_valid():
            order = serializer.save()
            transaction.on_commit(lambda:send_sms(order.id))
           
           
