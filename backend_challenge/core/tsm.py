"""Simple Travelling Salesperson Problem (TSP) between cities."""

import math
from math import sqrt
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
from geopy.geocoders import Nominatim
import numpy as np
from geopy.distance import great_circle, geodesic


"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Route:
    # gmaps = googlemaps.Client(key="WWWWW")

    # This computes the distance matrix by using GOOGLE MATRIX API

    """
    capacitated vehicle routing problem (CVRP) is a VRP in which vehicles
    with limited carrying capacity need to deliver items at various locations.
    The items have a quantity, such as weight or volume, and the vehicles have a maximum
    capacity that they can carry. The sees to is to  deliver the items for the
    least cost, while never exceeding the capacity of the vehicles.
    """

    num_vehicles = 0
    deliveries = None
    start_adress = None
    end_adress = None
    vehicle_capacity = 15
    locations = [(0, 0)]
    # demands = [0]

    def __init__(self, num, deliveries, start, capacity, locations):
        self.num_vehicles = num
        self.deliveries = deliveries
        self.start_adress = start
        # self.end_adress = end
        self.vehicle_capacity = capacity
        self.locations = locations

        # self.demands = demands

    # def compute_distance_matrix(self, overall_locations):
    #     # This computes the distance matrix by using GOOGLE MATRIX API
    #     response = self.gmaps.distance_matrix(
    #         overall_locations[0:], overall_locations[0:], mode="driving"
    #     )
    #     distance_matrix = np.zeros((len(overall_locations), len(overall_locations)))
    #     for index in range(1, len(overall_locations)):
    #         for idx in range(1, len(overall_locations)):
    #             distance_matrix[index, idx] = response["rows"][index - 1]["elements"][
    #                 idx - 1
    #             ]["distance"]["value"]

    #     return distance_matrix

    def compute_geodisic_distance_matrix(self, locations):
        # This computes the distance matrix by using geopy

        waypoints = [self.start_adress]

        for location in locations:
            waypoints.append(location)

        distance_matrix = [
            [(int(geodesic(p1, p2).miles)) for p2 in waypoints] for p1 in waypoints
        ]
        print(waypoints)
        return distance_matrix

    def create_data_model(self):
        """Stores the data for the problem."""

        data = {}
        data["distance_matrix"] = self.compute_geodisic_distance_matrix(self.locations)

        data["demands"] = [
            0,
            1,
            8,
            4,
            4,
            4,
            4,
            8,
            2,
            8,
            3,
        ]

        data["num_vehicles"] = 4
        data["vehicle_capacities"] = [15] * 4
        print(data["vehicle_capacities"])

        data["depot"] = 0
        return data

    def routing_solution(self, data, manager, routing, solution):
        """Prints solution on console."""
        print(f"Objective: {solution.ObjectiveValue()}")
        total_distance = 0
        total_load = 0
        routes = []
        paths = []

        operations = []
        for vehicle_id in range(data["num_vehicles"]):

            index = routing.Start(vehicle_id)
            plan_output = "Route {} for vehicle:".format(vehicle_id)
            route_distance = 0
            route_load = 0
            path = [manager.IndexToNode(index)]
            while not routing.IsEnd(index):

                node_index = manager.IndexToNode(index)

                route_load += data["demands"][node_index]
                plan_output += " {0} Load({1}) -> ".format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
                path.append(manager.IndexToNode(index))
                operation = {
                    "destination": manager.IndexToNode(index),
                    "capacity": data["demands"][manager.IndexToNode(index)],
                }
                operations.append(operation)
            print(operations)

            paths.append(path)

            plan_output += "Distance of the route: {}miles".format(route_distance)

            plan_output += "Load of the route: {}\n".format(route_load)

            routes.append(plan_output)

            roro=[(i, path) for (i,path) in enumerate(paths)]
            
            
               
            

            total_distance += route_distance
            total_load += route_load
        print("Total distance of all routes: {}m".format(total_distance))
        print("Total load of all routes: {}".format(total_load))

        return (
            routes,
            total_load,
            paths,
            roro
        )

    def generate_routes(self):
        """Solve the CVRP problem."""
        # Instantiate the data problem.
        data = self.create_data_model()

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Capacity constraint.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )
        # Add Distance constraint.
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(1)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            return self.routing_solution(data, manager, routing, solution)


locat = [
    (456, 320),  # location 0 - the depot
    (228, 0),  # location 1
    (912, 0),  # location 2
    (0, 80),  # location 3
    (114, 80),  # location 4
    (570, 160),  # location 5
    (798, 160),  # location 6
    (342, 240),  # location 7
    (684, 240),  # location 8
    (570, 400),  # location 9
    (912, 400),  # location 10
    (114, 480),  # location 11
    (228, 480),  # location 12
    (342, 560),  # location 13
    (684, 560),  # location 14
    (0, 640),  # location 15
    (798, 640),
]


overall_locations = [
    (-1.393864, 36.744238),  # RONGAI
    (-1.205604, 36.779606),  # RUAKA
    (-1.283922, 36.798107),  # Kilimani
    (-1.366859, 36.728069),  # langata
    (-1.311752, 36.698598),  # karen1  # karen2
    (-1.3362540729230734, 36.71637587249404),
    (-1.1752106333542798, 36.75964771015464),  # Banana1
    (-1.1773237686269944, 36.760334355612045),  # Banana2
]  #


# mato = compute_distance_matrix(overall_locations)


class Router:
    # capacity = 0
    # id = 0
    # adresses= []
    # last_name = 0
    # current_location = "0,0"

    def __init__(self, id, capacity, adresses):
        self.capacity = capacity
        self.adresses = adresses

    def compute_euclidean_distance_matrix(self, locations):
        locations = self.adresses
        """Creates callback to return distance between points."""
        distances = {}
        for from_counter, from_node in enumerate(locations):
            # print(from_node)
            distances[from_counter] = {}
            for to_counter, to_node in enumerate(locations):
                # print(to_node)
                if from_counter == to_counter:
                    distances[from_counter][to_counter] = 0
                else:
                    # Euclidean distance
                    distances[from_counter][to_counter] = int(
                        (
                            math.hypot(
                                (from_node[0] - to_node[0]), (from_node[1] - to_node[1])
                            )
                            * 100
                        )
                    )

        return distances

    # matriz = compute_euclidean_distance_matrix(overall_locations)
    # dm = [[(int(distance.distance(p1, p2).km)) for p2 in xy_list] for p1 in xy_list]
    def compute_distance_matrix(self):
        return [
            [(geodesic(p1, p2).miles) for p2 in self.adresses] for p1 in self.adresses
        ]

    def create_data_model(self):
        """Stores the data for the problem."""
        data = {}
        data["distance_matrix"] = self.compute_distance_matrix()

        # yapf: disable
        data['num_vehicles'] = 1
        data['depot'] = 0
        return data

    def print_solution(self, manager, routing, solution):
        """Prints solution on console."""
        print("Objective: {} km".format(solution.ObjectiveValue()))
        index = routing.Start(0)
        plan_output = "Route for vehicle 0:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += " {} ->".format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        plan_output += " {}\n".format(manager.IndexToNode(index))

        plan_output += "Route distance: {}km\n".format(route_distance)
        print(plan_output)
        return plan_output, route_distance

    def main(self):
        """Entry point of the program."""
        # Instantiate the data problem.
        data = self.create_data_model()

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic.

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30

        # search_parameters.first_solution_strategy = (
        #     routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        # )

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        # Print solution on console.
        if solution:
            return self.print_solution(manager, routing, solution)

    # def create_data_model():
    #     """Stores the data for the problem."""
    #     data = {}
    #     data["distance_matrix"] = matriz
    #     data["num_vehicles"] = 1
    #     data["depot"] = 0
    #     return data

    # def print_solution(manager, routing, solution):
    #     """Prints solution on console."""
    #     print("Objective: {} miles".format(solution.ObjectiveValue()))
    #     index = routing.Start(0)
    #     plan_output = "Route for vehicle 0:\n"
    #     routes = []
    #     route_distance = 0
    #     route = [manager.IndexToNode(index)]
    #     while not routing.IsEnd(index):
    #         plan_output += " {} ->".format(manager.IndexToNode(index))

    #         previous_index = index
    #         index = solution.Value(routing.NextVar(index))
    #         route_distance += (routing.GetArcCostForVehicle(previous_index, index, 0)/100)
    #         route.append(manager.IndexToNode(index))
    #     routes.append(route)
    #     plan_output += " {}\n".format(manager.IndexToNode(index))
    #     plan_output += "Route distance: {}miles\n".format(route_distance)
    #     route_path_cords = []
    #     for i in route:
    #         first = overall_locations[route[i]]
    #         print(first)
    #         route_path_cords.append(first)

    #     return routes, plan_output, route_path_cords

    # def main():
    #     """Entry point of the program."""
    #     # Instantiate the data problem.
    #     data = create_data_model()

    #     # Create the routing index manager.
    #     manager = pywrapcp.RoutingIndexManager(
    #         len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    #     )
    #     """_summary_

    #     Returns:
    #         _type_: _description_
    #     """
    #     # Create Routing Model.
    #     routing = pywrapcp.RoutingModel(manager)

    #     def distance_callback(from_index, to_index):
    #         """Returns the distance between the two nodes."""
    #         # Convert from routing variable Index to distance matrix NodeIndex.
    #         from_node = manager.IndexToNode(from_index)
    #         to_node = manager.IndexToNode(to_index)
    #         return data["distance_matrix"][from_node][to_node]

    #     transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    #     # Define cost of each arc.
    #     routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    #     # Setting first solution heuristic.
    #     search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    #     search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    #     search_parameters.local_search_metaheuristic = (
    #         routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    #     )
    #     search_parameters.time_limit.seconds = 30

    #     # search_parameters.first_solution_strategy = (
    #     #     routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    #     # )

    #     # Solve the problem.
    #     solution = routing.SolveWithParameters(search_parameters)

    #     # Print solution on console.
    #     if solution:
    #         return print_solution(manager, routing, solution)

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
