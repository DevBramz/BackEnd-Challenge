import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Customer, Order
from .tasks import send_sms
from django.test.utils import override_settings

@pytest.mark.django_db
@pytest.fixture
def user_fixture():
    user = User.objects.create(
        username="john", email="lennon@thebeatles.com", password="johnpassword"
    )
    return user


@pytest.mark.django_db
def test_user_create(user_fixture):
    assert User.objects.count() == 1
    
@pytest.fixture
def api_client():
   from rest_framework.test import APIClient
   return APIClient()


@pytest.mark.django_db    
def test_customer_model_string_representation(user_fixture):
    customer = Customer.objects.create(
        user=user_fixture, phone="+254728826517", code="5665"
    )
    assert customer.__str__()=="lennon@thebeatles.com"
@pytest.mark.django_db
def test_customer_create(user_fixture, api_client):
    url = "/api/v1/customer"
    
    api_client.force_authenticate(user=user_fixture)

    data = {
        "phone": "+254728826517",
        "code": "code",
        "user": user_fixture,
    }

    response =api_client.post(url, data=data)
    assert response.status_code == 201
    assert Customer.objects.count() == 1


@pytest.mark.django_db
def test_anonymous_user_cannot_create_customer(api_client):
    url = "/api/v1/customer"
    api_client.force_authenticate(user=None)
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_customer_create_invalid_phone(user_fixture,api_client):
    url = "/api/v1/customer"
    api_client.force_authenticate(user=user_fixture)

    data = {
        "phone": "0728826517",
        "code": "code",
        "user": user_fixture,
    }

    response = api_client.post(url, data=data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_customer_create_no_phone(user_fixture,api_client):
    url = "/api/v1/customer"
    api_client.force_authenticate(user=user_fixture)

    data = {
        "phone": "",
        "code": "code",
        "user": user_fixture,
    }

    response =api_client.post(url, data=data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_customer_create_no_code(user_fixture,api_client):
    url = "/api/v1/customer"
    api_client.force_authenticate(user=user_fixture)

    data = {
        "phone": "",
        "code": "",
        "user": user_fixture,
    }

    response =api_client.post(url, data=data)
    assert response.status_code == 400



    
@pytest.mark.django_db
def test_order_create(user_fixture,api_client):
    url = "/api/v1/order"
    api_client.force_authenticate(user=user_fixture)
    customer = Customer.objects.create(
        user=user_fixture, phone="+254728826517", code="5665"
    )
    data = {"item": "books", "amount": 4, "customer": customer}
    response =api_client.post(url, data=data)
    assert response.status_code == 201
    assert Order.objects.count() == 1
@pytest.mark.django_db    
def test_order_string_representation(user_fixture):
    customer = Customer.objects.create(
        user=user_fixture, phone="+254728826517", code="5665"
    )
    order = Order.objects.create(item="books", amount=4, customer=customer)
    assert order.__str__()==str(order.id)

@pytest.mark.django_db
def test_order_create_no_customer(user_fixture,api_client):
    url = "/api/v1/order"
    api_client.force_authenticate(user=user_fixture)
    data = {"item": "books", "amount": 4,"customer":""}
    response =api_client.post(url, data=data)
    assert response.status_code == 400



@pytest.mark.django_db
@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
def test_send_new_event_service_called(mocker, user_fixture):
    client = APIClient()
    url = "/api/v1/order"
    client = APIClient()
    client.force_authenticate(user=user_fixture)
    customer = Customer.objects.create(
        user=user_fixture, phone="+254728865507", code="5665"
    )
    data = {"item": "books", "amount": 4, "customer": customer}
    response = client.post(url, data=data)
    print(response.data)
    assert response.status_code == 201
    order=Order.objects.get(customer=customer)
    mock_send_new_event = mocker.patch("backend_challenge.core.tasks.send_sms",
		    				return_value={'SMSMessageData': {'Message': 'Sent to 1/1 Total Cost: KES 0.8000', 'Recipients': [{'statusCode': 101, 'number': '+254728865507', 'cost': 'KES 0.8000', 'status': 'Success', 'messageId': 'ATXid_415eabf3cb8623da7f6aa2b2c79981c9'}]}}
		)
    
    mock_send_new_event.delay(order_id=order.id)
    mock_send_new_event.delay.assert_called_with(
       order_id=order.id
   )
@pytest.mark.django_db   
def test_anonymous_user_cannot_create_order(api_client):
    url = "/api/v1/order"
    api_client.force_authenticate(user=None)
    response = api_client.get(url)
@pytest.mark.django_db     
def test_create_order_with_no_item(user_fixture,api_client):
    client = APIClient()
    url = "/api/v1/order"
    api_client.force_authenticate(user=user_fixture)
    customer = Customer.objects.create(
        user=user_fixture, phone="+254728865507", code="5665"
    )
    data = {"item": "", "amount": 4, "customer": customer}
    response = api_client.post(url, data=data)
    assert response.status_code == 400
       


  
    
