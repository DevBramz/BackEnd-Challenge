import csv
import json
from django.http import HttpResponse,JsonResponse
from backend_challenge.core.Router import CVRP
from backend_challenge.core.exceptions import CVRPException, RoutingException
from backend_challenge.core.utilization import LoadOptimization
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
from .models import Delivery, Driver, RouteSettings, Trip
from .serializers import RouteSettingsSerializer, DeliverySerializer, ContactForm, TripSerializer
from .tasks import send_sms_recepient
from django.template.defaultfilters import slugify
from rest_framework.reverse import reverse
from django.shortcuts import redirect,render
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError




def index(request):
    return render(request, 'deliveries.html')

def trips(request):
    return render(request, 'trips.html')

def update_settings(request, id):
    settings = get_object_or_404(RouteSettings, id=id)
    
    return render(request, 'update_settings.html')

def view_route_summary(request):
    
    return render(request, 'summary.html')





class DeliveryViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    serializer_class = DeliverySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["code", "status"]
    # renderer_classes = [TemplateHTMLRenderer]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        qs = Delivery.objects.all()

        return qs

    def list(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    # data = {'deliveries': queryset}
    # return Response(data, template_name='deliveries.html')

    @action(detail=True)
    def assign(self, request, pk=None):
        """
        Method to assign an order to delivery
        """
        delivery = self.get_object()
        available_drivers = Driver.objects.filter(availability_status=True)
        if available_drivers.exists():
            driver = available_drivers.first()
            delivery = self.get_object()
            delivery.assign(driver)

            driver.availability_status = False
            driver.save()

            data = {
                "delivery_id": delivery.id,
                "order_code": delivery.code,
                "url": reverse("core:delivery-detail", args=[pk], request=request),
                "assignedto": driver.name,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            not_found = {"errors": "No drivers available."}
            return Response(data=not_found, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['POST'],)   
    def get_selected(self, request):
        
        ids = request.data.get("ids")
        # if not ids:
        #     raise ValidationError("No deliveries were selected")
        id_list=json.loads(ids)
        request.session["selected"]=ids
        deliveries=Delivery.objects.filter(
                    code__in=id_list
                )
        serializer = self.get_serializer(deliveries, many=True)
        return Response(serializer.data)
        
        
        

    # @action(detail=False)
    # def export_deliveries(self, request, *args, **kwargs):
    #     """
    #     Method to export orders
    #     """
    #     queryset = self.filter_queryset(self.get_queryset())
    #     print(queryset)

    #     return self.export(queryset)
    # https://www.quora.com/Can-a-software-engineer-use-one-company-source-code-in-another-company-If-not-why

    @action(detail=False)
    def bulk_assign(self, request, *args, **kwargs):
        """
        Method to export orders
        """
        data = request.data
        data2 = request.POST.getlist("data")

        selected_ids = data.get("data", None)
        if selected_ids:

            with transaction.atomic():
                for i in selected_ids:
                    key = i["id"]
                    delivery = Delivery.objects.get(id=key)
                    available_drivers = Driver.objects.filter(availability_status=True)
                    if available_drivers.exists():
                        driver = available_drivers.first()
                        delivery.assign(driver)
                        driver.update(availability_status=False)

            return Response(data)

        else:
            return

    @action(detail=True)
    def clone(self, request, pk=None):
        """
        Method to clone an order
        """
        delivery = self.get_object()
        delivery.pk = None
        delivery._state.adding = True

        delivery.save()

        if delivery:
            data = {
                "id": delivery.id,
                "code": delivery.code,
                "status": delivery.status,
                "weight": delivery.weight,
                "address": delivery.address,
                "url": reverse(
                    "core:delivery-detail", args=[delivery.id], request=request
                ),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for creating route settings and generating
    routes
    """

    queryset = RouteSettings.objects.all()
    serializer_class = RouteSettingsSerializer
    
class TripViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for trip crud 
    """

    queryset = Trip.objects.filter(status='dispatched').order_by("-edited")
    serializer_class = TripSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["code", "status"]



# def update(self, request, *args, **kwargs):
#    data = request.POST.getlist("data")
#     data = request.DATA
#     qs = Student_academic_program.objects.filter(student=2773951)
#     serializer = StudentAcademicProgramSerializer(qs, data=data, many=True)

#     if serializer.is_valid():
#         serializer.save()

#         return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])  # policy decorator
# data = request.POST.getlist("data")
# @renderer_classes([JSONRenderer])       # policy decorator
# def items_not_done(request):
#     user_count = Item.objects.filter(done=False).count()
#     content = {'not_done': user_count}

#     return Response(content)
# https://github.com/lafifii/cvrp


class Contact(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'drivers.html'

    def get(self, request):
        queryset = Driver.objects.all()
        return Response({'drivers': queryset})
    # serializer_class = ContactForm

    # def get(self, request, **kwargs):
    #     """
    #     Get the entire edit history for a comment
    #     :param request:
    #     :param kwargs:
    #     :return:
    #     """
    #     data = request.data

    #     serializer = self.serializer_class(data)

    #     return Response(serializer.data, status.HTTP_200_OK)
@api_view()
def plan_routes(request):
    selected_delivery_codes=request.session.get("selected")

    if not selected_delivery_codes:
        raise RoutingException
    
        
    codes_list=json.loads(selected_delivery_codes)
    deliveries=Delivery.objects.filter(
                    code__in=codes_list
                )
        
    optimization_settings=RouteSettings.objects.get(org__name="ibuQA")
    print(optimization_settings.id)
    # settings=model_to_dict(optimization_settings)
    # settings=RouteSettingsSerializer(optimization_settings).data
   
    
    

    all_drivers = Driver.objects.all().order_by("id")
    start=optimization_settings.start_address
            
    if optimization_settings.selection == "Min_Distance":
                    drivers = all_drivers
                    

                    route = CVRP(
                        drivers,
                        deliveries,
                        start,
                    )  # Rout

    elif optimization_settings.selection == "Min_Veh":

                    optimization = LoadOptimization(deliveries, all_drivers)
                    list_of_ids = optimization.main()

                    drivers = all_drivers.filter(
                        pk__in=list_of_ids)
                    
                    
                    
                    route = CVRP(
                        drivers,
                        deliveries,
                        start,
                    )  # Rout
                    
        
    routes_summary= route.generate_routes()
    trip_data=routes_summary.get("routes",None)
        
      

        
        
    request.session["trip_data"] = trip_data
    # print(summary)
    # context = {'route_summary': summary}
    # summary_json=json.dumps(summary)
    # print(summary_json)
    # data=summary
    
    # return JsonResponse(data, safe=False)
   
    # return render(request, 'summary.html',context)
    return Response(trip_data)
    # return redirect('/api/v1/dispatch')

    
    
    
    
    
    
   
    
    

@api_view()
def dispatch_routes(request):
    """
    Creates and dispatches trip from routes
    """
    routes = request.session.get("trip_data", None)
    

    if routes:
        with transaction.atomic():
            for i, route in enumerate(routes):
                driver = route["driver_name"]
                driver = Driver.objects.get(name=driver)

                load = route["load"]
                vehicle_utilization =route["vehicle_capacity_utilization"]
                utilization = str(vehicle_utilization)
                distance = route["distance"]
                tasks = route["deliveries"]
                deliverys = Delivery.objects.filter(code__in=tasks)
                num_deliveries = str(deliverys.count())

                trip = Trip.objects.create(
                        load=load,
                        utilization=utilization,
                        distance=distance,
                        driver=driver,
                        num_deliveries=num_deliveries,
                        # departure_time=departure_time
                       
                        
                    )
                trip.dispatch()
            #   send sms  post save signal
               
                
                
                for delivery in deliverys:
                    delivery.trip = trip
                    delivery.status = "dispatched"
                    delivery.phone='+254728826517'
                    delivery.save()
                    # trip.deliveries_in_trip.add(delivery)
                    # send_sms_recepient(delivery.id)
                # transaction.on_commit(lambda:send_sms_recepient.delay(delivery))
                    
            # print(trip.deliveries_in_trip.all())
            
            del request.session["trip_data"]
            del request.session["selected"]
            return Response({"message": "Trip_created"})
    raise Exception('No Trip data')
  
class SettingsDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'settings_detail.html'

    def get(self, request):
        settings = RouteSettings.objects.last()
        serializer = RouteSettingsSerializer(settings)
        return Response({'serializer': serializer, 'settings': settings})

    def post(self, request,):
        settings = RouteSettings.objects.last()
        serializer = RouteSettingsSerializer(settings, data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'settings': settings})
        serializer.save()
        return redirect('/api/v1/route_summary')    


#  def post(self, request, *args, **kwargs):
#         order_items = {
#             'items': []
#         }

#         items = request.POST.getlist('items[]')

#         for item in items:
#             menu_item = MenuItem.objects.get(pk__contains=int(item))
#             item_data = {
#                 'id': menu_item.pk,
#                 'name': menu_item.name,
#                 'price': menu_item.price
#             }

#             order_items['items'].append(item_data)

#             price = 0
#             item_ids = []

#         for item in order_items['items']:
#             price += item['price']
#             item_ids.append(item['id'])

#         order = OrderModel.objects.create(price=price)
#         order.items.add(*item_ids)

#         context = {
#             'items': order_items['items'],
#             'price': price
#         }

#         return render(request, 'customer/order_confirmation.html', context)
