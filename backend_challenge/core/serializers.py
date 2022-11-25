from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Customer, Order
from django.core.exceptions import ObjectDoesNotExist


class CustomerProfileUnavailable(APIException):
    """Exception raised when customer profile  is not present in the data."""
    status_code = 404
    # default_detail = 'Service temporarily unavailable, try again later.'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("phone", "code")


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("item", "amount", "customer")

    def create(self, validated_data):
        """
        Create a new Order instance, given the accepted data
        and with the request user
        """
        request = self.context.get("request", None)
        
        if request is None:
            return False
        # customer=get_object_or_404(Customer, user=user)
        if "customer" not in validated_data:
            try:
                validated_data["customer"] = request.user.customer
                
            except ObjectDoesNotExist as snip_no_exist:
                raise CustomerProfileUnavailable() from snip_no_exist

        

        return Order.objects.create(**validated_data)
