from celery import shared_task
from django.shortcuts import get_object_or_404


from .exceptions import SmsException
from rest_framework.exceptions import APIException, NotFound, ValidationError
import africastalking


username = "sandbox"  # use 'sandbox' for development in the test environment
api_key = "c9f005c42d219254395dcdf172419336c2412e27acf3c98e4bca321bc7138341"
from .models import Delivery

africastalking.initialize(username, api_key)


@shared_task
def send_sms_recepient(delivery_id):

    """

    Task to send an sms notification when an order is
    successfully created.
    """

    # if not r:
    #     raise Exception('Wrong API key ')

    sms = africastalking.SMS
    if not sms:
        raise Exception("Error Sending Sms")

    # queryset = Order.objects.select_related("customer").all()
    # delivery= get_object_or_404(Delivery, id=delivery_id)
    delivery = Delivery.objects.get(id=delivery_id)

    message = f"Dear Your order {delivery.id} is expected to be delivered at ETA ."
    response = sms.send(message, [delivery.phone])
    print(response)
    if not response:
        raise Exception("Could not send messge")
    return response

@shared_task
def send_sms_driver(message, driver_phone):

    """

    Task to send an sms notification when an order is
    successfully created.
    """

    """_summary_

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    # if not r:
    #     raise Exception('Wrong API key ')

    sms = africastalking.SMS
    if not sms:
        raise Exception("Error Sending Sms")

    # queryset = Order.objects.select_related("customer").all()
    # delivery= get_object_or_404(Delivery, id=delivery_id)

    response = sms.send(message, [driver_phone])
    try:
        response = sms.send(
            "Hey AT Ninja!", ["+254728826517"]
        )  # Enter your phone number here
        print(response)
    except Exception as e:
        print(f"Something went wrong {e}")
        return response


#    sudo service redis-server stop
# $ celery -A backend_challenge worker -l INFO
# coverage run --omit 'venv/*' -m pytest && coverage report -m
