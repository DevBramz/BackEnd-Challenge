"""Simple Travelling Salesperson Problem (TSP) between cities."""

import math
from math import sqrt
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
import numpy as np
from geopy.distance import great_circle, geodesic
import polyline

from backend_challenge.core.exceptions import SmsException, RoutingException


class CVRP:  # pragma: no cover
    # gmaps = googlemaps.Client(key="WWWWW")

    # This computes the distance matrix by using GOOGLE MATRIX API

    """
    capacitated vehicle routing problem (CVRP) is a VRP in which vehicles
    with limited carrying capacity need to deliver items at various locations.
    The items have a quantity, such as weight or volume, and the vehicles have a maximum
    capacity that they can carry. The sees to is to  deliver the items for the
    least cost, while never exceeding the capacity of the vehicles.
    """

    drivers = []
    deliveries = []
    start_adress = None
    end_adress = None
    capacity = 0

    def __init__(self, drivers, deliveries, start):
        self.drivers = drivers
        self.deliveries = deliveries
        self.start_adress = start

    def compute_distance_matrix(self, overall_locations):
        """This computes the distance matrix by using GOOGLE MATRIX API"""
        response = self.gmaps.distance_matrix(
            overall_locations[0:], overall_locations[0:], mode="driving"
        )
        distance_matrix = np.zeros((len(overall_locations), len(overall_locations)))
        for index in range(1, len(overall_locations)):
            for idx in range(1, len(overall_locations)):
                distance_matrix[index, idx] = response["rows"][index - 1]["elements"][
                    idx - 1
                ]["distance"]["value"]

        return distance_matrix

    def all_waypoints(self):
        """
        returns a list of waypoints including the start adress a in optimization settings
        To be used in calcuation of distance matrix
        """
        teamhub_dict_adress = {
            "adress_name": "Kilimani",
            "latlong": self.start_adress,
        }  # fetch adress from team hub

        waypoints = [teamhub_dict_adress] + [
            delivery.location for delivery in self.deliveries
        ]
        return waypoints

    def compute_geodisic_distance_matrix(self):
        """computes the distance matrix by using geopy"""

        waypoints = [waypoint["latlong"] for waypoint in self.all_waypoints()]
        distance_matrix = [
            [(int(geodesic(p1, p2).miles)) for p2 in waypoints] for p1 in waypoints
        ]
        return distance_matrix

    def create_data_model(self):
        """Stores the data for the problem."""

        data = {}
        data["distance_matrix"] = self.compute_geodisic_distance_matrix()

        data["demands"] = [
            0,  # the quantity of the delivery in each delivery adress
            3,  # use deelivery.quantity for deliveries
            7,
            4,
            9,
            4,
            8,
            4,
            2,
            4,
            7,
        ]

        data[
            "num_vehicles"
        ] = self.drivers.count()  # for better and faster queries than usinglen()
        data["vehicle_capacities"] = list(
            self.drivers.values_list("capacity", flat=True)
        )  # flat=True return list   from queryset object more perfornamnt

        data["depot"] = 0
        return data

    def routing_solution(self, data, manager, routing, solution):
        """returns rouing soluting"""

        total_distance = 0
        total_load = 0
        routes = []

        operations = []
        path_cordinates = []
        for vehicle_id in range(data["num_vehicles"]):
            route_data = {}

            index = routing.Start(vehicle_id)
            plan_output = "Route {} for :".format(vehicle_id)
            route_distance = 0
            route_load = 0
            route_id = vehicle_id + 1
            path = [manager.IndexToNode(index)]

            locations = self.all_waypoints()

            while not routing.IsEnd(index):

                node_index = manager.IndexToNode(index)

                route_load += data["demands"][node_index]
                plan_output += " {0} Load({1}) -> ".format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
                route_data["vehicle"] = route_id
                driver_names = list(self.drivers.values_list("name", flat=True))
                route_data["driver_name"] = driver_names[route_id]
                route_data["load"] = route_load
                route_data["distance"] = route_distance

                # route_data["vehicle_capacity_utilization"] =

                path.append(manager.IndexToNode(index))
            path_adresses = [locations[i]["adress_name"] for i in path]
            path_cordinates = [locations[i]["latlong"] for i in path]
            encoded_polyline = polyline.encode(path_cordinates, 5)
            route_data["route"] = path_adresses
            route_data["encoded_polyline"] = encoded_polyline

            plan_output += "Distance of the route: {}miles".format(route_distance)

            plan_output += "Load of the route: {}\n".format(route_load)

            routes.append(plan_output)
            operations.append(route_data)
            for route_data in operations:
                # Cleans the data to remove the route data if the distance==0
                if route_data["distance"] == 0:
                    operations.remove(route_data)

            total_distance += route_distance
            total_load += route_load
            payload = {
                "total_distance": total_distance,
                "total_load": total_load,
                "num_vehicles_used": len(operations),
                "solution": operations,
            }

        return (
            payload,
            routes,
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
        search_parameters.time_limit.FromSeconds(5)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            return self.routing_solution(data, manager, routing, solution)

        else:
            # hould return routing failed and log the error(logger.info(routing.status()))
            raise RoutingException
