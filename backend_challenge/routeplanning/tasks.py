import africastalking
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from fleets.models import Driver, DriverProfile
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


username = "tumahub"  # use 'sandbox' for development in the test environment
api_key = "a816f60c32aa85edf422d9001b0463b18627fd034670217b15d33d300258894d"


class SmsException(Exception):
    """Exception raised SMS is not sent"""

    message = ""

    def __init__(self, msg) -> None:
        self.message = msg


africastalking.initialize(username, api_key)
sms = africastalking.SMS
if not sms:
    raise SmsException("Error Sending Sms")


# @celery_app.task()
def assign_driver_sms(driver_id, trip_url):
    """

    Task to send an sms notification when an order is
    successfully created.

    """
    driver = Driver.objects.get(id=driver_id)
    user = driver.org_user.user
    message = (
        f"hello ,{user.name} You have a new trip request.Click here to view {trip_url}"
    )

    response = sms.send(message, [driver.phone])
    if not response:
        raise SmsException("Error Sending Sms")

    return message


# def driver_order_assignment(trip):
#     # if trip.state != "Awaiting_Assignment":
#     #     return False
#     #  driver status is idle., and driver vehicle type is requested and
#     origin_point = trip.stops.first()
#     pnt = origin_point.coords
#     nearest_drivers=DriverProfile.objects.filter(point__distance_lte=(pnt, D(km=10))).order_by(
#         "distance"
#     )
#     print(trip.state)


# def send_recepient_delivered_sms(shipment_id):
#     """

#     Task to send an sms notification when an order is
#     successfully delivered.
#     """
#     africastalking.initialize(username, api_key)

#     sms = africastalking.SMS
#     if not sms:
#         raise SmsException("Error Sending Sms")

#     queryset = Shipment.objects.select_related("recepient", "sender").all()
#     shipment = get_object_or_404(queryset, id=shipment_id)

#     message = f"Hi {shipment.recepient.name},! We've received an update that your package from {shipment.sender.name}  has been delivered. Feel free to leave a review here: http://bit.ly/p1we1"
#     print(message)
#     response = sms.send(message, [shipment.recepient.phone_number])
#     if not response:
#         raise SmsException("Error Sending Sms")

#     return message


#    sudo service redis-server stop
# $ celery -A tuma worker -l INFO
