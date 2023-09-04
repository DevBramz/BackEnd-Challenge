import africastalking
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from shipments.models import Shipment

from config import celery_app

# @celery_app.task()
# def get_users_count():
#     """A pointless Celery task to demonstrate usage."""
#     return User.objects.count()


class SmsException(Exception):
    """Exception raised SMS is not sent"""

    message = ""

    def __init__(self, msg) -> None:
        self.message = msg


username = "sandbox"  # use 'sandbox' for development in the test environment
api_key = "c24b10b049468747684e01f846e1a7420e106584c144d187b62d39fe667b6a78"


# @celery_app.task()
# @async_to_sync
def send_dispatch_sms(shipment_id):
    """

    Task to send an sms notification when an order is
    successfully created.
    """
    africastalking.initialize(username, api_key)

    sms = africastalking.SMS
    # if not sms:
    #     raise SmsException("Error Sending Sms")

    # queryset = Shipment.objects.select_related("recepient", "sender").all()
    # shipment = await Shipment.objects.select_related("recepient", "sender").aget(
    #     id=shipment_id
    # )
    shipment = Shipment.objects.select_related("recepient", "sender").get(
        id=shipment_id
    )
    # domain = sync_to_async(Site.objects.get_current().domain, thread_sensitive=False)
    # tracking_url = f"http://{domain}/tracking/package/{shipment.tracking_id}"
    # tracking_url = await shipment.tracking_url()

    message = f"Hi {shipment.recepient.name}, Your package from {shipment.sender.name } is on its way to you! Track it here:{shipment.tracking_url}"
    print(message)
    # response = sms.send(message, [shipment.recepient.phone_number])
    # if not response:
    #     raise SmsException("Error Sending Sms")

    return message


#    sudo service redis-server stop
# $ celery -A tuma worker -l INFO
