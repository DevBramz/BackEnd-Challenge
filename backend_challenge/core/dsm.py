# Envisioned and defined by Razvan Manescu

import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps

import config





class Router:
    gmaps = googlemaps.Client(key=config.GOOGLE_API_KEY)

    # This computes the distance matrix by using GOOGLE MATRIX API
    def compute_distance_matrix(self, overall_locations):
        response = self.gmaps.distance_matrix(overall_locations[1:], overall_locations[1:], mode='driving')
        distance_matrix = np.zeros((len(overall_locations), len(overall_locations)))

        for index in range(1, len(overall_locations)):
            for idx in range(1, len(overall_locations)):
                distance_matrix[index, idx] = response['rows'][index - 1]['elements'][idx - 1]['distance']['value']

        return distance_matrix

    # This computes the distance between two locations using GOOGLE DIRECTIONS API
    # And it is used to compute the distance matrix if the above method is not used
    def compute_distance(self, first_location, second_location):
        google_maps_api_result = self.gmaps.directions(first_location,
                                                       second_location,
                                                       mode='driving')
        return google_maps_api_result[0]['legs'][0]['distance']['value']

    # This computes the model given an array of Orders and an array of Drivers
    def compute_data_model(self, orders, drivers):
        overall_locations = [(0, 0)]
        demands = [0]
        pickups_deliveries = []
        driver_initial_locations = []
        driver_capacities = []
        order_for_node = {}

        for order in orders:
            overall_locations.append(order.pick_up_address)
            overall_locations.append(order.drop_off_address)
            pickups_deliveries.append([len(overall_locations) - 2, len(overall_locations) - 1])
            order_for_node[len(overall_locations) - 2] = order
            order_for_node[len(overall_locations) - 1] = order
            demands.append(order.quantity)
            demands.append(-1 * order.quantity)

        for driver in drivers:
            overall_locations.append(driver.current_location)
            driver_initial_locations.append(len(overall_locations) - 1)
            driver_capacities.append(driver.capacity)
            demands.append(0)

        if config.GOOGLE_API_USED == "DIRECTIONS":
            distance_matrix 1= np.zeros((len(overall_locations), len(overall_locations)))
            for index in range(1, len(overall_locations)):
                for idx in range(1, len(overall_locations)):
                    distance_matrix[index, idx] = self.compute_distance(overall_locations[index],
                                                                        overall_locations[idx])
        else:
            distance_matrix1 = self.compute_distance_matrix(overall_locations)
         

        data = {
                'num_drivers': len(driver_capacities),
                'depot': 0,
                'demands': demands,
                'driver_capacities': driver_capacities,
                "driver_maximum_distance": 9000000000,
                'distance_matrix': distance_matrix,
                'pickups_deliveries': pickups_deliveries,
                'time_limit_seconds': config.SEARCH_TIME_LIMIT,
                'driver_initial_locations': driver_initial_locations,
                'driver_return_locations': [0] * len(driver_capacities),
                'order_for_node': order_for_node,
                'drivers': drivers
         }

        return data

    def print_solution(self, data, manager, routing, solution):
        total_distance = 0
        total_load = 0
        for driver_id in range(data['num_drivers']):
            index = routing.Start(driver_id)
            plan_output = 'Route for vehicle {}:\n'.format(driver_id)
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data['demands'][node_index]
                plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, driver_id)
            plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                     route_load)
            plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            plan_output += 'Load of the route: {}\n'.format(route_load)
            print(plan_output)
            total_distance += route_distance
            total_load += route_load
        print('Total distance of all routes: {}m'.format(total_distance))
        print('Total load of all routes: {}'.format(total_load))

    # This constructs an object/dictionary containing the solution, ready to be formatted to json
    def construct_response(self, data, manager, routing, solution):
        response = {'drivers_and_operations': []}

        for driver_id in range(data['num_drivers']):
            index = routing.Start(driver_id)
            index = solution.Value(routing.NextVar(index))
            operations = []
            route_length = 0

            while not routing.IsEnd(index):
                route_length = route_length + 1
                index = solution.Value(routing.NextVar(index))

            index = routing.Start(driver_id)
            index = solution.Value(routing.NextVar(index))

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                operation = {
                        'order': data['order_for_node'][node_index].__dict__,
                        'priority': route_length,
                        'type': 'ridicare' if data['demands'][node_index] > 0 else 'livrare'
                }
                operations.append(operation)
                route_length = route_length - 1
                index = solution.Value(routing.NextVar(index))

            driver_and_operations = {
                'driver': data['drivers'][driver_id].__dict__,
                'operations': operations
            }
            response['drivers_and_operations'].append(driver_and_operations)

        return response

    def obtain_routes_for(self, orders, drivers):

        # Instantiate the data problem.
        data = self.compute_data_model(orders, drivers)

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_drivers'], data['driver_initial_locations'],
                                               data['driver_return_locations'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Define cost of each arc.
        def distance_callback(from_index, to_index):
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # This defines a constrain, by specifying the  demand of  each node
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)
        dimension_name = 'Capacity'
        # This defines a constrain, by specifying the  maximum capacity for each driver,
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['driver_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        dimension_name = 'Distance'
        # This defines a constrain, the maximum distance for each driver,
        # This should be a large distance, it shouldn't be taken into account
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            data["driver_maximum_distance"],  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)

        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        count_dimension_name = 'Count'
        # This defines a constrain, the maximum nodes to be visited by each driver,
        # just to distribute fairly the orders to all the available drivers
        routing.AddConstantDimension(
            1,  # increment by one every time
            len(data["distance_matrix"][0]) // len(data['driver_capacities']) + 1,
            # max value forces equivalent # of jobs
            True,  # set count to zero
            count_dimension_name)

        # Define Transportation Requests.
        for request in data['pickups_deliveries']:
            pickup_index = manager.NodeToIndex(request[0])
            delivery_index = manager.NodeToIndex(request[1])
            routing.AddPickupAndDelivery(pickup_index, delivery_index)
            routing.solver().Add(
                routing.VehicleVar(pickup_index) == routing.VehicleVar(
                    delivery_index))
            routing.solver().Add(
                distance_dimension.CumulVar(pickup_index) <=
                distance_dimension.CumulVar(delivery_index))

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

        # search for global if intended
        if config.SEARCH_STRATEGY == 'GLOBAL':
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

        search_parameters.log_search = config.LOG_SEARCH
        search_parameters.time_limit.seconds = data['time_limit_seconds']

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Return solution in the form of a response.
        if solution:
            return self.construct_response(data, manager, routing, solution)
        else:
            return "ERROR"
        
    # https://stackoverflow.com/questions/45733763/pytest-run-tests-parallel   
          # class OrderShipmentSerializer(serializers.HyperlinkedModelSerializer):
    #     class Meta:
    #         model = OrderShipment
    #         fields = (
    #             "created",
    #             "code",
    #             "item",
    #             "amount",
    #             "status",
    #             "customer",
    #             "category",
    #         )

    # def create(self, validated_data):
    #     """
    #     Create a new Order instance, given the accepted data
    #     and with the request user
    #     """
    #     request = self.context.get("request", None)

    #     if request is None:
    #         return False
    #     # customer=get_object_or_404(Customer, user=user)
    #     if "customer" not in validated_data:
    #         try:
    #             validated_data["customer"] = request.user.customer

    #         except ObjectDoesNotExist as snip_no_exist:
    #             raise CustomerProfileUnavailable() from snip_no_exist

    #     return Order.objects.create(**validated_data)

    # from django.db import models


# STATE_CREATED = "created"
# STATE_ = ""
# STATE_TO_AIRPORT = "to_airport"
# STATE_TO_HOTEL = "to_hotel"
# STATE_DROPPED_OFF = "dropped_off"


#     0 - created
#     1 - assigned
#     2 - on_the_way
#     3 - checked_in
#     4 - done
#     5 - this status is not in use
#     6 - accepted
#     7 - canceled
#     8 - rejected
#     9 - unacknowledged


# STATE_CHOICES = (
#     (STATE_REQUEST, STATE_REQUEST),
#     (STATE_WAITING, STATE_WAITING),
#     (STATE_TO_AIRPORT, STATE_TO_AIRPORT),
#     (STATE_TO_HOTEL, STATE_TO_HOTEL),
#     (STATE_DROPPED_OFF, STATE_DROPPED_OFF),
# )

# TRANSITIONS = {
#     STATE_REQUEST: [STATE_WAITING,],
#     STATE_WAITING: [STATE_REQUEST, STATE_TO_AIRPORT],
#     STATE_TO_AIRPORT: [STATE_TO_HOTEL, STATE_REQUEST],
#     STATE_TO_HOTEL: [STATE_DROPPED_OFF],
#     STATE_DROPPED_OFF: [],
# }


# class Pickup(models.Model):
#     __current_state = None

#     state = models.CharField(
#         max_length=20, choices=STATE_CHOICES, default=STATE_REQUEST
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.__current_state = self.state

#     def save(
#         self,
#         force_insert=False,
#         force_update=False,
#         using=None,
#         update_fields=None,
#     ):
#         allowed_next = TRANSITIONS[self.__current_state]

#         updated = self.state != self.__current_state
#         if self.pk and updated and self.state not in allowed_next:
#             raise Exception("Invalid transition.", self.state, allowed_next)

#         if self.pk and updated:
#             self.__current_state = self.state

#         return super().save(
#             force_insert=force_insert,
#             force_update=force_update,
#             using=using,
#             update_fields=update_fields,
#         )

#     def _transition(self, state):
#         self.state = state
#         self.save()

#     def assign(self, driver):
#         # we omit storing the driver on the model for simplicity of the example
#         self._transition(STATE_WAITING)

#     def accept(self):
#         self._transition(STATE_TO_AIRPORT)

#     def decline(self):
#         self._transition(STATE_REQUEST)

#     def picked_up(self):
#         self._transition(STATE_TO_HOTEL)

#     def dropped_off(self):
#         self._transition(STATE_DROPPED_OFF)
# class User(AbstractUser):
#     photo = models.ImageField(upload_to='photos', null=True, blank=True)

#     @property
#     def group(self):
#         groups = self.groups.all()
#         return groups[0].name if groups else None


# def get_or_assign_number(self):
#         if self.number is None:
#             epoch = datetime.now().date()
#             epoch = epoch.replace(epoch.year, 1, 1
#             qs = Order.objects.filter(number__isnull=False, created_at__gt=epoch)
#             qs = qs.aggregate(models.Max('number'))
#             try:
#                 epoc_number = int(str(qs['number__max'])[4:]) + 1
#                 self.number = int('{0}{1:05d}'.format(epoch.year, epoc_number))
#             except (KeyError, ValueError):
#                 # the first order this year
#                 self.number = int('{0}00001'.format(epoch.year))
#         return self.get_number(){
# "destinations": ["(41.878876, -87.635918)","(41.8848274, -87.6320859)"]

 # maximum number of tasks per route
    # https://support.onfleet.com/hc/en-us/articles/360023910351-Route-Optimization-Operating
    # https://planner.myrouteonline.com/route-planner/
    # https://routific.com/
    # https://www.bringg.com/blog/dispatching/delivery-route-planner-app-what-you-need-know/
    # https://www.bringg.com/resources/guides/route-optimization-software/
    # https://www.bringg.com/resources/guides/route-optimization-software/
    # https://cloud.google.com/blog/products/maps-platform/how-use-distance-matrix-api
    # https://developers.google.com/maps/documentation/transportation-logistics/on-demand-rides-deliveries-solution/trip-deliveries-progress/fleet-engine
    # https://hvitis.dev/geolocation-tutorial-geodjango-demo-and-gis-postgis-data-to-build-app-using-rest-api
    # https://hvitis.dev/geolocation-tutorial-geodjango-demo-and-gis-postgis-data-to-build-app-using-rest-api
    # key=AIzaSyDABJug6DRDa_H1xmu1xxI9FLpdwWmhf3Y&callback=initAutocomplete&libraries=places&v=weekly"
    # CREATE USER geodjango PASSWORD 'lucy';


# CREATE DATABASE geodjango OWNER geodjango;
# CREATE DATABASE geodjango WITH OWNER
# https://www.alibabacloud.com/blog/setting-up-a-postgresql-database-on-an-ubuntu-instance_594124;
# https://www.alibabacloud.com/blog/setting-up-a-postgresql-database-on-an-ubuntu-instance_594124;
# maximum no of deliveries;proof of delivery, Delivery_window,no of vehicldes
# No entrance windows, bad weather, high traffic hours, and unexpected route obstructions can all significantly slow down your delivery. As a result, it’s critical to use dynamic delivery route optimization software that calculates and assigns the most effective delivery routes.
# https://sandesh-deshmane.medium.com/architecture-and-design-principles-for-online-food-delivery-system-33bfda73785d
# Set your preferred optimization goal.
# Minimum distance
# Minimum time
# Balance time and distance
# Balance time and distance
# You have 20 trucks (more than enough to hold all the items) and you want to use the fewest trucks that will hold them all.
# Automatic dispatch and asignment#automatic dispatch assumes all drivers are available


# Keep deliveries as i


# sudo -i -u postgres
# Routes API is the next generation, performance optimized version of the existing Directions API and Distance Matrix API. It helps you find the ideal route from A to Z, calculates ETAs and distances for matrices of origin and destination locations, and also offers new features.
#     if mode not in ["driving", "walking", "bicycling", "transit"]:
#             raise ValueError("Invalid travel mode."

