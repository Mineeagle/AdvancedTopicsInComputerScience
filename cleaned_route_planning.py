import requests
import json
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from osm_connector import OSMConnector
from maps_link_generator import MapsLinksGenerator


class RoutePlanning:
    def __init__(self, kippemuehle=(50.982761, 7.118816)):
        """
        This class is used to calculate the route.

        Please make the import parameter 'kippmuehle' your starting
        and endpoint (coordinates again)
        """
        self.osm_connector = self._get_osm_graph_connector()
        self.kippemuehle = kippemuehle

    def get_google_maps_link(self):
        """
        Returns the google maps link for the route
        """
        return MapsLinksGenerator.get_link(self.kippemuehle, self._get_route())

    def _get_osm_graph_connector(self):
        """
        Use the OSMConnector class to allows fetching data from
        Open Street Maps.
        """
        return OSMConnector(
            (50.991172, 7.123864), "bergischGladbach.graphml", 5000, False
        )

    def _fetch_web_data(self):
        """
        Fetch data from website to use for the navigation
        """
        link = "https://altkleider.davidhojczyk.de/api/container/list"
        result = requests.get(link)
        data_dict = json.loads(str(result.text))
        return data_dict

    def _get_distance_matrix(self, filled_containers):
        """
        Returns the distance matrix between every point.
        (This also includes the starting point.)
        """
        # Load the coordinates of every container and the starting point
        coordinates = [self.kippemuehle]
        for container in filled_containers:
            coordinates.append((container["lat"], container["lon"]))

        # Calculate matrix
        result = []
        for container in coordinates:
            result_list = []
            for sub_container in coordinates:
                result_time = int(
                    self.osm_connector.get_fastest_time_in_seconds(
                        container, sub_container
                    )
                )
                result_list.append(result_time)
            result.append(result_list)
        return result

    def _get_data_for_route_building(self):
        """
        Get the needed data for the route calculations

        !!!
        A few assumptions have been made when it comes to the vehicle:
        We only use one, and if the amount of stuff to get is above the
        (amount of vehicles * vehicle capacity constant), this calculation breaks.
        !!!

        """
        # Get information about the containers above a certain value
        full_containers = [
            container for container in self._fetch_web_data() if container["fill"] >= 20
        ]

        # Construct the needed data
        data = {}
        data["demands"] = [container["fill"] for container in full_containers]
        data["demands"].insert(0, 0)
        data["distance_matrix"] = self._get_distance_matrix(full_containers)
        data["num_vehicles"] = 12
        data["vehicle_capacities"] = [250 for vehicle in range(data["num_vehicles"])]
        data["depot"] = 0
        return data

    def _get_route(self):
        data = self._get_data_for_route_building()

        """
        This method, as well as the method '_get_solution' are modified versions
        of the code which can be found here:
        https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/samples/vrp_capacity.py
        From here on, the code does its magic.
        """

        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            data["vehicle_capacities"],
            True,
            "Capacity",
        )
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(1)
        solution = routing.SolveWithParameters(search_parameters)
        if solution:
            return self._get_solution(data, manager, routing, solution)

    def _get_solution(self, data, manager, routing, solution):
        """
        Please refer to '_get_route'
        """
        result_ids = []
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                """The line below is important for us"""
                # Get indices of the containers to convert them back to the coordinates
                result_ids.append(manager.IndexToNode(index))
                route_load += data["demands"][node_index]
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )

            total_distance += route_distance
            total_load += route_load

        # If there are stops with zero beforehand, remove them
        # This can happen due to the shenanigans we did with the vehicles
        # and their capacity
        output_list = []
        already_non_zero_found = False
        for entry in result_ids:
            if entry == 0:
                if not already_non_zero_found:
                    continue
            already_non_zero_found = True
            output_list.append(entry)

        # Grab with the inidces the correct coordinates and return them
        full_containers = [
            container for container in self._fetch_web_data() if container["fill"] >= 20
        ]

        coords_route = []
        for route_index in output_list:
            if route_index == 0:
                coords_route.append(self.kippemuehle)
            else:
                coords_route.append(
                    (
                        full_containers[route_index - 1]["lat"],
                        full_containers[route_index - 1]["lon"],
                    )
                )

        return coords_route

