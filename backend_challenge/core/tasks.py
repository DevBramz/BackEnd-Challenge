from celery import shared_task
from django.shortcuts import get_object_or_404
from .exceptions import SmsException
from rest_framework.exceptions import APIException, NotFound, ValidationError
import africastalking
# from .models import Order




    
username = "sandbox"    # use 'sandbox' for development in the test environment
api_key = "c24b10b049468747684e01f846e1a7420e106584c144d187b62d39fe667b6a78"


    


@shared_task
def send_sms(order_id):
    
    """
  
    Task to send an sms notification when an order is
    successfully created.
    """
    africastalking.initialize(username, api_key)


    sms = africastalking.SMS
    if not sms:
        raise SmsException("Error Sending Sms")
    
    # queryset = Order.objects.select_related("customer").all()
    # order = get_object_or_404(queryset, id=order_id)
    
    # message = f"Dear {order.customer} You have successfully placed an order.Your order ID is {order.id}."
    # response = sms.send(message, [order.customer.phone])
    response=sms.send()
    if not response:
         raise SmsException("Error Sending Sms")
        
    return response
#    sudo service redis-server stop
# $ celery -Abackend_challenge worker -l INFO
# coverage run --omit 'venv/*' -m pytest && coverage report -m



