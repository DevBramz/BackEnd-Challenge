import json

import requests
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
from .tasks import send_sms


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
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            raise NotFound("Please Create Customer Profile")
        return self.queryset.filter(customer=customer)

    def perform_create(self, serializer):
        if serializer.is_valid():
            order = serializer.save()
            send_sms(order.id)
           
