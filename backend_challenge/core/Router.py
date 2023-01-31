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
from .models import Trip

from backend_challenge.core.exceptions import (
    SmsException,
    RoutingException,
    CVRPException,
)


class CVRP:  # pragma: no cover
    api_key = "AIzaSyBxI_rtVjyCashC_RtMxOuZnrRorwKc34M"

    gmaps = googlemaps.Client(key=api_key)
    print(gmaps)
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

    def overall_locations(self):
        """
        returns a list of all deliveries locations + depot adress including the start adress a in optimization settings
        To be used in calcuation of distance matrix
        """
        teamhub_dict_adress = {
            "code":"depot",
            "adress_name": "Kilimani",  # fetch adress from team hub, hardcorded for demo #integration
            "latlong": self.start_adress,
        }  # fetch adress from team hub
        
        if not teamhub_dict_adress:
            raise CVRPException("could not get teamhub adress")
        overall_locations = [teamhub_dict_adress] + [
            delivery.location for delivery in self.deliveries
        ]
        if not overall_locations:
            raise CVRPException("could not get overall locations")
        return overall_locations

    def compute_geodisic_distance_matrix(self):
        """computes the distance matrix by using geopy"""

        overall_locations = [
            waypoint["latlong"] for waypoint in self.overall_locations()
        ]  # list of waypints cordinates
        if not overall_locations:
            raise CVRPException("could not getoverall_locations latlong")

        distance_matrix = [
            [(int(geodesic(p1, p2).miles)) for p2 in overall_locations]
            for p1 in overall_locations
        ]
        if not distance_matrix:
            raise CVRPException("could not calculate matriz")
        return distance_matrix

    def compute_distance_matrix(self):
        """This computes the distance matrix by using GOOGLE MATRIX API"""
        overall_locations = [
            waypoint["latlong"] for waypoint in self.overall_locations()
        ]
        print(overall_locations)
        # response = self.gmaps.distance_matrix(
        #     overall_locations[0:], overall_locations[0:], mode="driving"
        # )
        response={
            "destination_addresses": ["Lexington, MA, USA", "Concord, MA, USA"],
            "origin_addresses": ["Boston, MA, USA", "Charlestown, Boston, MA, USA"],
            "rows": [
                {
                    "elements": [
                        {
                            "distance": {"text": "33.3 km", "value": 33253},
                            "duration": {"text": "27 mins", "value": 1620},
                            "duration_in_traffic": {"text": "34 mins", "value": 2019},
                            "status": "OK",
                        },
                        {
                            "distance": {"text": "41.5 km", "value": 41491},
                            "duration": {"text": "33 mins", "value": 1981},
                            "duration_in_traffic": {"text": "39 mins", "value": 2342},
                            "status": "OK",
                        },
                    ],
                },
                {
                    "elements": [
                        {
                            "distance": {"text": "31.1 km", "value": 31100},
                            "duration": {"text": "26 mins", "value": 1543},
                            "duration_in_traffic": {"text": "29 mins", "value": 1754},
                            "status": "OK",
                        },
                        {
                            "distance": {"text": "39.3 km", "value": 39338},
                            "duration": {"text": "32 mins", "value": 1904},
                            "duration_in_traffic": {"text": "35 mins", "value": 2077},
                            "status": "OK",
                        },
                    ],
                },
            ],
            "status": "OK",
        }
        # l
        # distance_matrix = np.zeros((len(overall_locations), len(overall_locations)))
        # for index in range(1, len(overall_locations)):
        #     for idx in range(1, len(overall_locations)):
        #         distance_matrix[index, idx] = response["rows"][index - 1]["elements"][
        #             idx - 1
        #         ]["distance"]["value"]
        # print(distance_matrix)
        
        distance_matrix = []
        for row in response['rows']:
            row_list = [row['elements'][j]['duration_in_traffic']['value'] for j in range(len(row['elements']))]
            distance_matrix.append(row_list)
        return distance_matrix

        
    def create_data_model(self):
        """Stores the data for the problem."""

        data = {}
        data["distance_matrix"] = self.compute_geodisic_distance_matrix()
        
        print(data["distance_matrix"])

        data["demands"] = [0] + list(self.deliveries.values_list("weight", flat=True))
        # the quantity of the delivery in each delivery adress

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

            locations = self.overall_locations()

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
                driver_dict = self.drivers.values()
                driver_name=driver_dict[vehicle_id]["name"]
                route_data["driver_name"] = driver_name

                route_data["distance"] = route_distance
                route_data["load"] = route_load
                route_data["duration"] = "not calculated"

                driver_capacity = driver_dict[vehicle_id]["capacity"]
                vehicle_utilization = int((route_load / driver_capacity) * 100)

                route_data["vehicle_capacity_utilization"] = vehicle_utilization

                # route_data["vehicle_capacity_utilization"] =[((route_load/driver["capacity"])*100)for driver in drivers_dict]
                # print(route_data["vehicle_capacity_utilization"])
               
                   

                path.append(manager.IndexToNode(index))
            path_adresses = [locations[i]["adress_name"] for i in path]
            deliveries = [locations[i]["code"] for i in path[1:(len(path)-1)]]
            path_cordinates = [locations[i]["latlong"] for i in path]
            encoded_polyline = polyline.encode(path_cordinates, 5)
            route_data["num_deliveries"] = len(deliveries) 
            route_data["deliveries"] = deliveries
            route_data["route"] = path_adresses
            route_data["encoded_polyline"] = encoded_polyline

            plan_output += "Distance of the route: {}miles".format(route_distance)

            plan_output += "Load of the route: {}\n".format(route_load)

            routes.append(plan_output)
            operations.append(route_data)
            
            for route_data in operations[:]:
                # Cleans the data to remove the route data if the distance==0
                if route_data["distance"] == 0:
                    operations.remove(route_data)
            
            
                
            

            total_distance += route_distance
            total_load += route_load

            payload = {
                "total_distance": total_distance,
                "total_load": total_load,
                "num_vehicles_used": len(operations),
                "routes": operations,
                "summary": routes,
            }
        
        for i in range(len(operations)):
            trip_data=operations[i]
            deliveries=operations[i]
            code=trip_data["vehicle"]
            driver=trip_data["driver_name"]
            rider=self.drivers.get(name=driver)
               
            load=trip_data["load"]
            vehicle_utilization= trip_data["vehicle_capacity_utilization"]
            utilization=str(vehicle_utilization)
            distance= trip_data["distance"]

               
            Trip.objects.create(code=code,load=load,utilization=utilization,distance=distance,rider=rider)
            
        return (payload,)

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
            30000000,  # vehicle maximum travel distance
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
        raise RoutingException

        # should return routing failed and log the error(logger.info(routing.status()))
