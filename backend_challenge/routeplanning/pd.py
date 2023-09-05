"""Simple Travelling Salesperson Problem (TSP) between cities."""

import json
import logging
import math
import time
import urllib
from datetime import date, datetime, timedelta
from itertools import groupby
from math import sqrt

import googlemaps
import numpy as np
import requests
from django.contrib.gis.geos import GEOSGeometry, LineString, Point
from django.contrib.sessions.backends.db import SessionStore
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from geopy.distance import geodesic, great_circle
from haversine import Unit, haversine
from locations.models import Location
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from shipments.serializers import ShipmentSerializer

# import googlemaps
# import numpy as np
# import polyline
from core.exceptions import CVRPException, RoutingException

# from .models import Trip

logger = logging.getLogger(__name__)

gmaps = googlemaps.Client(key="AIUnBxaNSfxaCyVXdIIm7aGK")


class CVRPD:
    """
    capacitated vehicle routing,Pickup and Delivery problem (CVRPD) is a VRP in which vehicles
    with limited carrying capacity need to  pick up items at various locations and
drops them off at others. . The items have a quantity, such as weight or volume, and the vehicles have a maximumcapacity that they can carry. which each vehicle picks up items at various locations and drops them off at others. The problem is to assign routes for the vehicles to pick up and deliver all the items, while minimizing the length of the longest route.The sees to is to  deliver the items for the
    least cost, while never exceeding the capacity of the vehicles.
    """

    over_locations = [(0, 0)]
    drivers = []
    shipments = []
    optimization_settings = None
    capacity = 0

    def __init__(
        self,
        drivers,
        shipments,
        start_address,
        start_latlong,
        start_cords,
        departure_time,
    ):
        self._drivers = drivers

        self._shipments = shipments
        # self.optimization_settings = optimization_settings
        self.start_address = start_address
        self.departure_time = departure_time
        self.start_latlong = start_latlong
        self.start_cords = start_cords


    @property
    def shipments(self):
        return self._shipments

    @property
    def drivers(self):
        return self._drivers

    @property
    def overall_locations(self):
        """
        returns a list of all shipments locations + depot adress including the start adress a in optimization settings
        To be used in calcuation of distance matrix
        """
        # point = [coord for coord in self.optimization_settings.start_point.l]
        # start = point[::-1]

        teamhub_dict_adress = {
            "address": self.start_address,
            "latlong": self.start_latlong,
            "point": self.start_cords,
        }
        # fetch adress from team hub
        if not teamhub_dict_adress:
            raise CVRPException("could not get teamhub adress")
        overall_locations = [teamhub_dict_adress]
        for shipment in self.shipments:
            overall_locations.append(shipment.origin.location_info)
            overall_locations.append(shipment.destination.location_info)
        if not overall_locations:
            raise CVRPException("could not get overall locations")
        return overall_locations

    @property
    def compute_geodisic_distance_matrix(self):
        """computes the distance matrix by using geopy"""

        overall_locations = [waypoint["latlong"] for waypoint in self.overall_locations]
        if not overall_locations:
            raise CVRPException("could not getoverall_locations latlong")

        distance_matrix = [
            [(int(geodesic(p1, p2).km)) for p2 in overall_locations]
            for p1 in overall_locations
        ]
        if not distance_matrix:
            raise CVRPException("could not calculate matrix")

        return distance_matrix

    # This computes the distance matrix by using GOOGLE MATRIX API
    gmaps = googlemaps.Client(key="AIzaSyCxPhWHPyUnBxaNSfxaCyVXdIIm7aGKmTY")

 

    def compute_time_matrix(self, overall_locations):
        # This computes and retuens both distance and time matrix by using GOOGLE MATRIX API
        response = self.gmaps.distance_matrix(
            overall_locations, overall_locations, mode="driving"
        )
        time_matrix = []
        for row in response["rows"]:
            row_list = [
                row["elements"][j]["duration"]["value"]
                for j in range(len(row["elements"]))
            ]
            time_matrix.append(row_list)
        return time_matrix

    def compute_geodisic_distance_matrix2(self, overall_locations):
        """computes the distance matrix by using geopy"""

        distance_matrix = [
            [(int(geodesic(p1, p2).km)) for p2 in overall_locations]
            for p1 in overall_locations
        ]

        if not distance_matrix:
            raise CVRPException("could not calculate matrix")
        return distance_matrix

   

    def compute_time_matrix(self, overall_locations):
        matrix_data = {}
        time_matrix = []
        distance_matrix = []

        # time_matrix=[]

        addresses = overall_locations

        # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
        max_elements = 100
        num_addresses = len(addresses)  # 16 in this example.
        # Maximum number of rows that can be computed per request ().
        max_rows = max_elements // num_addresses
        # num_addresses = q * max_rows + r ().
        q, r = divmod(num_addresses, max_rows)
        dest_addresses = addresses
        time_matrix = []
        # Send q requests, returning max_rows rows per request.
        for i in range(q):
            origin_addresses = addresses[i * max_rows : (i + 1) * max_rows]
            response = self.gmaps.distance_matrix(
                origin_addresses, dest_addresses, mode="driving"
            )
            time_matrix += self.build_time_matrix(response)
            distance_matrix += self.build_distance_matrix(response)
            matrix_data["time_matrix"] = time_matrix
            matrix_data["distance_matrix"] = distance_matrix

        # Get the remaining remaining r rows, if necessary.
        if r > 0:
            origin_addresses = addresses[q * max_rows : q * max_rows + r]
            response = self.gmaps.distance_matrix(
                origin_addresses, dest_addresses, mode="driving"
            )
            time_matrix += self.build_time_matrix(response)
            distance_matrix += self.build_distance_matrix(response)

            matrix_data["time_matrix"] = time_matrix
            matrix_data["distance_matrix"] = distance_matrix

        return matrix_data

    def build_time_matrix(self, response):
        time_matrix = []
        for row in response["rows"]:
            row_list = [
                row["elements"][j]["duration"]["value"]
                for j in range(len(row["elements"]))
            ]

            time_matrix.append(row_list)
        return time_matrix

    def build_distance_matrix(self, response):
        distance_matrix = []
        for row in response["rows"]:
            row_list = [
                row["elements"][j]["distance"]["value"]
                for j in range(len(row["elements"]))
            ]
            rowlist2 = [i / 1000 for i in row_list]

            distance_matrix.append(rowlist2)
        return distance_matrix

    

    def create_data_model(self):
        """Stores the data for the problem."""

       
        latlong = self.start_latlong # start latlong object
        overall_locations = [latlong]
        demands = [0]
        pickups_deliveries = []
        # starts = []
        # ends = []
        vehicle_capacities = []
        shipment_for_node = {}

        for shipment in self._shipments:
            overall_locations.append(shipment.origin.latlong)
            overall_locations.append(shipment.destination.latlong)
            pickups_deliveries.append(
                [len(overall_locations) - 2, len(overall_locations) - 1]
            )
            shipment_for_node[len(overall_locations) - 2] = shipment
            shipment_for_node[len(overall_locations) - 1] = shipment
            demands.append(int(shipment.weight))
            demands.append(-1 * (int(shipment.weight)))

        for driver in self.drivers:
           
            vehicle_capacities.append(driver.driver_profile.capacity)

            

        matrix_data = self.compute_time_matrix(overall_locations)

        # for i in range(len(distance_matrix)):
        #     distance_matrix[i][0] = 0

        time_matrix = matrix_data["time_matrix"]
     
        distance_matrix = matrix_data["distance_matrix"]
     

        data = {
            "num_vehicles": len(vehicle_capacities),
            "depot": 0,
            "demands": demands,
            "vehicle_capacities": vehicle_capacities,
            "driver_maximum_distance": 9000000000000000,
            "distance_matrix": distance_matrix,
            "time_matrix": time_matrix,
            "pickups_deliveries": pickups_deliveries,
            # "time_limit_seconds": config.SEARCH_TIME_LIMIT,
            # "driver_initial_locations": driver_initial_locations,
            "starts": [0] * len(vehicle_capacities),
            "ends": [0] * len(vehicle_capacities),
            "shipment_for_node": shipment_for_node,
            "drivers": self._drivers,
        }

        return data

    def routing_solution(self, data, manager, routing, solution):
        """returns rouing soluting"""

        # Display dropped nodes.
        dropped_shipments = []
        dropped_nodes = "Dropped nodes:"
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if solution.Value(routing.NextVar(node)) == node:
                dropped_nodes += " {}".format(manager.IndexToNode(node))
                dropped_shipment = data["shipment_for_node"][manager.IndexToNode(node)]
                dropped_shipments.append(dropped_shipment.code)

        time_dimension = routing.GetDimensionOrDie("Time")
        total_time = 0
        total_distance = 0
        total_load = 0
        routes = []

        operations = []

        for vehicle_id in range(data["num_vehicles"]):
            route_data = {}

            index = routing.Start(vehicle_id)
            # summary_id = vehicle_id + 1
            # plan_output = "Route {}  :".format(summary_id)
            route_distance = 0
            route_load = 0
            route_time = 0
            departure_time = self.departure_time

            route_stops = []
            route_etas = []
            _etas = []

            route_id = vehicle_id + 1
            path = [manager.IndexToNode(index)]

            # route_path["path"] = path

            locations = self.overall_locations

            # stop_sequence = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                # dt.timedelta(seconds = value)

                time_var = time_dimension.CumulVar(node_index)

                route_time = solution.Min(time_var)

                # _eta=datetime.combine(date.today(), departure_time) + timedelta(minutes=route_time)
                _eta = (departure_time + timedelta(seconds=route_time)).strftime(
                    "%a %d %b %Y, %I:%M%p"
                )

                route_etas.append(route_time)
                _etas.append(_eta)

                point = locations[node_index]["point"]
                stop = Location.objects.get(cords=point)
                stop_info = {
                    "stop_eta": _eta,
                    "stop_address": stop.address,
                    "stop_latlong": stop.latlong,
                }

                # stop_sequence += 1

                route_load += data["demands"][node_index]

                # plan_output += " {0}  Load ({1}) -> ".format(place, route_load)
                # plan_output += " {0}   -> ".format(place)
                previous_index = index

                index = solution.Value(routing.NextVar(index))

                # distance = routing.GetArcCostForVehicle(
                #     previous_index, index, vehicle_id
                # )
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )

                route_data["vehicle"] = route_id
                driver_dict = self._drivers.values()
                driver_name = driver_dict[vehicle_id]["displayName"]

                route_data["driver_name"] = driver_name

                route_data["distance"] = route_distance
                # route_data["load"] = route_load

                # driver_capacity = driver_dict[vehicle_id]["capacity"]
                # route_data["vehicle_capacity"] = driver_capacity
                # vehicle_utilization = int((route_load / driver_capacity) * 100)
                # route_data["vehicle_capacity"] = driver_capacity

                # route_data["vehicle_capacity_utilization"] = vehicle_utilization

                # route_data["vehicle_capacity_utilization"] =[((route_load/driver["capacity"])*100)for driver in drivers_dict]

                path.append(manager.IndexToNode(index))
                route_stops.append(stop_info)
            time_var = time_dimension.CumulVar(index)
            total_time = solution.Min(time_var)
            route_est = (departure_time + timedelta(seconds=total_time)).strftime(
                "%a %d %b %Y, %I:%M%p"
            )
            route_etas.append(total_time)

            # route_stops.append(stop_dict)

            path_adresses = [locations[i]["address"] for i in path]
            last_adress = path_adresses[-1]
            last_stop = Location.objects.get(address=last_adress)

            end_stop = {
                "stop_eta": route_est,
                "stop_address": last_stop.address,
                "stop_latlong": last_stop.latlong,
            }

            route_stops.append(end_stop)
            stop_data = [i[0] for i in groupby(route_stops)]
            stop_adresses = [i[0] for i in groupby(path_adresses)]
            shipments_in_route = [
                ShipmentSerializer(data["shipment_for_node"][i]).data
                for i in path[1:-1]
            ]

        
            route_data["num_stops"] = len(stop_adresses) - 1
            # route_data["stops"] = stops
            route_data["path"] = stop_adresses

            route_data["route_shipments"] = json.dumps(
                shipments_in_route, cls=DjangoJSONEncoder
            )
            route_data["duration"] = total_time
            route_data["departure_time"] = departure_time.strftime(
                "%a %d %b %Y, %I:%M%p"
            )
            route_data["load"] = route_load
            # route_data["encoded_polyline"] = encoded_polyline
            route_data["stops"] = stop_adresses
            route_data["stop_data"] = stop_data
            route_data["est"] = route_est
            operations.append(route_data)

            for route_data in operations[:]:
                # Cleans the data to remove the route data if the distance==0
                if route_data["distance"] == 0:
                    operations.remove(route_data)

            total_distance += route_distance
            total_load += route_load

            payload = {
                "num_vehicles_used": len(operations),
                "dropped_shipments": set(dropped_shipments),
                "summary": routes,
                "routes": operations,
            }

        return payload

    def generate_routes(self):
        """Solve the CVRP problem."""
        # Instantiate the data problem.

        data = self.create_data_model()

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(
            len(data["time_matrix"]), data["num_vehicles"], data["starts"], data["ends"]
        )

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)
        # Allow to drop nodes.
        penalty = 1_000_000
        for node in range(1, len(data["distance_matrix"])):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

        def time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            # Convert from routing variable Index to time matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["time_matrix"][from_node][to_node]

        # self._total_time[from_node][to_node] = int(
        #                 self.service_time(data, from_node) + self.travel_time(
        #                     data, from_node, to_node))

        time_callback_index = routing.RegisterTransitCallback(time_callback)

        time = "Time"
        routing.AddDimension(
            time_callback_index,
            100,  # allow waiting time
            100000000000,  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            time,
        )
        time_dimension = routing.GetDimensionOrDie(time)

        for i in range(data["num_vehicles"]):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i))
            )
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.End(i))
            )

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
            300000000000000000,  # vehicle maximum travel distance calculate from route settings
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Define Transportation Requests.
        for request in data["pickups_deliveries"]:
            pickup_index = manager.NodeToIndex(request[0])
            delivery_index = manager.NodeToIndex(request[1])
            routing.AddPickupAndDelivery(pickup_index, delivery_index)
            routing.solver().Add(
                routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index)
            )
            routing.solver().Add(
                distance_dimension.CumulVar(pickup_index)
                <= distance_dimension.CumulVar(delivery_index)
            )

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(10)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.re
        if solution:
            return self.routing_solution(data, manager, routing, solution)
        logger.info(routing.status())
        raise RoutingException

        # should return routing failed and log the error(logger.info(routing.status()))

        
