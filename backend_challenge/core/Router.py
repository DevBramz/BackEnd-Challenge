"""Simple Travelling Salesperson Problem (TSP) between cities."""

import math
from math import sqrt
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
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
    capacity = 0

    def __init__(self, num, deliveries, start, capacity):
        self.num_vehicles = num
        self.deliveries = deliveries
        self.start_adress = start
        self.capacity = capacity

    def compute_distance_matrix(self, overall_locations):
        """ This computes the distance matrix by using GOOGLE MATRIX API """
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
        """returns a list of waypoints including the start adress a in optimization settings"""
        waypoints = [self.start_adress] + [
            delivery.location for delivery in self.deliveries
        ]
        return waypoints

    def compute_geodisic_distance_matrix(self):
        """computes the distance matrix by using geopy"""
      
        waypoints = self.all_waypoints()
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

        data["num_vehicles"] = self.num_vehicles
        data["vehicle_capacities"] = [self.capacity] * self.num_vehicles

        data["depot"] = 0
        return data

    def routing_solution(self, data, manager, routing, solution):
        """returns rouing soluting"""

        total_distance = 0
        total_load = 0
        routes = []

        operations= []
        path_cordinates = []
        for vehicle_id in range(data["num_vehicles"]):
            route_data = {}

            index = routing.Start(vehicle_id)
            plan_output = "Route {} for vehicle:".format(vehicle_id)
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
                route_data["route"] = route_id
                route_data["load"] = route_load
                route_data["distance"] = route_distance
                path.append(manager.IndexToNode(index))

            path_cordinates = [locations[i] for i in path]
            route_data["path"] = path_cordinates

            plan_output += "Distance of the route: {}miles".format(route_distance)

            plan_output += "Load of the route: {}\n".format(route_load)

            routes.append(plan_output)
            operations.append(route_data)
            for route_data in operations:
                #Cleans the data to remove the roy=ute data if the distance==0
                if route_data["distance"]==0:
                    operations.remove(route_data) 
                
           

            total_distance += route_distance
            total_load += route_load

        return (
            routes,
            operations,
            total_load,
            total_distance,
            
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
        search_parameters.time_limit.FromSeconds(10)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            return self.routing_solution(data, manager, routing, solution)
        else:
            msg = "Could not generate route path"
            return {"msg": msg}
