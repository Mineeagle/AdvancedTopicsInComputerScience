import osmnx as ox
import networkx as nx
import requests
import json
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class MapsLinksGenerator:
    @staticmethod
    def get_link(start_end_location, waypoints):
        result_link = "https://www.google.com/maps/dir/?api=1"
        result_link += f"&origin={start_end_location[0]},{start_end_location[1]}"
        if len(waypoints) > 0:
            result_link += "&waypoints="
            for waypoint in waypoints:
                result_link += f"{waypoint[0]},{waypoint[1]}|"
            result_link = result_link[:-1]
        result_link += f"&destination={start_end_location[0]},{start_end_location[1]}"

        return result_link


class OSMConnector:
    def __init__(
        self,
        location_coordinates: tuple,
        graph_file_path="foo.graphml",
        dist=1000,
        simplify=True,
        network_type="drive",
    ):
        """
        This class is the connection to OpenStreetMaps (OSM).
        It allows to easily get the shortest distance / the fastest travel time needed between to coordinates.
        Coordinates are represented by a tuple, which looks like this: (lat, long)

        These are the importing parameters:
        location_coordinates: tuple => the general location of the node_system (coordinates)
        graph_file_path: str => the string to save the graph data to. Allows to reload the data.
            Please note though, that should the variables like location_coordinates change, this file has to be deleted manually.
        dist: int => the amount of distance in meters around the location coordinates
        simplify: bool => should the graph be simplified? makes it less accurate, but also faster
        network_type: str => mode of transportation
        """
        assert graph_file_path.endswith(".graphml")
        "The graph file path is invalid and needs to end with '.graphml"

        try:
            self.graph = ox.load_graphml(graph_file_path)
        except FileNotFoundError:
            self.graph = ox.graph_from_point(
                location_coordinates,
                dist=dist,
                simplify=simplify,
                network_type=network_type,
            )
            self.graph = ox.add_edge_speeds(self.graph)
            self.graph = ox.add_edge_travel_times(self.graph)
            ox.save_graphml(self.graph, graph_file_path)

    def get_fastest_time_in_seconds(self, origin_coordinates, destination_coordinates):
        """
        Returns the time needed to drive through the fastest route
        """
        origin_node = self._convert_coordinates_to_node(origin_coordinates)
        destination_node = self._convert_coordinates_to_node(destination_coordinates)
        return nx.shortest_path_length(
            self.graph, origin_node, destination_node, weight="travel_time"
        )

    def get_shortest_distance_in_meters(
        self, origin_coordinates, destination_coordinates
    ):
        """
        Returns the time needed to drive the fastest route
        """
        origin_node = self._convert_coordinates_to_node(origin_coordinates)
        destination_node = self._convert_coordinates_to_node(destination_coordinates)
        return nx.shortest_path_length(
            self.graph, origin_node, destination_node, weight="length"
        )

    def _convert_coordinates_to_node(self, coordinates):
        """
        Returns the nearest node that is in the graph
        """
        return ox.nearest_nodes(self.graph, Y=coordinates[0], X=coordinates[1])


class RoutePlanning:
    def __init__(self, kippemuehle=(50.982761, 7.118816)):
        """
        This class is used to calculate the route.

        Please make the import parameter 'kippmuehle' your starting
        and endpoint (coordinates again)
        """
        self.osm_connector = OSMConnector(
            (50.991172, 7.123864), "bergischGladbach.graphml", 5000, False
        )
        self.kippemuehle = kippemuehle

    def get_google_maps_link(self):
        """
        Returns the google maps link for the route
        """
        return MapsLinksGenerator.get_link(self.kippemuehle, self._get_route())

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


if __name__ == "__main__":
    rp = RoutePlanning()
    print(rp.get_google_maps_link())