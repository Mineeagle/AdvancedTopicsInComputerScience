import requests
import json
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from osm_connector import OSMConnector
from maps_link_generator import MapsLinksGenerator


class Route_planing:
    def __init__(self, kippemuehle=(50.982761, 7.118816)):
        self.osm_connected = self.osm_connection()
        self.kippemuehle = kippemuehle
        waypoints = self.get_route()
        link = MapsLinksGenerator.get_link(kippemuehle, waypoints)
        print(link)

        # Matrix aufstellen

    def _get_data(self):
        # Datenverbindung aufbauen (runterladen)
        link = "https://altkleider.davidhojczyk.de/api/container/list"
        result = requests.get(link)
        data_dict = json.loads(str(result.text))
        return data_dict

    def osm_connection(self):
        bergisch_gladbach_connect = OSMConnector(
            (50.991172, 7.123864), "bergischGladbach.graphml", 5000, False
        )
        return bergisch_gladbach_connect

    def get_coords(self, filled_containers):
        coordsList = [self.kippemuehle]
        for container in filled_containers:
            coordsList.append((container["lat"], container["lon"]))
        return coordsList

    def get_matrix(self, filled_containers):
        coordinates = self.get_coords(filled_containers)
        result = []

        for container in coordinates:
            result_list = []
            for sub_container in coordinates:
                result_time = int(
                    self.osm_connected.get_fastest_time_in_seconds(
                        container, sub_container
                    )
                )
                result_list.append(result_time)
                # print(result_time)
            result.append(result_list)
            # print (result_string)
        return result

    def get_data(self):
        web_information = self._get_data()
        full_containers = self.cleanup(web_information)
        data = {}
        data["demands"] = [container["fill"] for container in full_containers]
        data["demands"].insert(0, 0)
        data["distance_matrix"] = self.get_matrix(full_containers)
        data["num_vehicles"] = 12
        data["vehicle_capacities"] = [250 for vehicle in range(data["num_vehicles"])]
        data["depot"] = 0
        return data

    def cleanup(self, web_information):
        result = []
        for container in web_information:
            if container["fill"] <= 20:
                continue
            result.append(container)
        return result

    def get_solution(self, data, manager, routing, solution):
        """Prints solution on console."""
        print(f"Objective: {solution.ObjectiveValue()}")
        result_ids = []
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                result_ids.append(manager.IndexToNode(index))
                route_load += data["demands"][node_index]
                plan_output += f" {node_index} Load({route_load}) -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            plan_output += f" {manager.IndexToNode(index)} Load({route_load})\n"

            plan_output += f"Distance of the route: {route_distance}m\n"
            plan_output += f"Load of the route: {route_load}\n"
            print(plan_output)
            total_distance += route_distance
            total_load += route_load
        print(f"Total distance of all routes: {total_distance}m")
        print(f"Total load of all routes: {total_load}")

        output_list = []
        already_non_zero_found = False
        for entry in result_ids:
            if entry == 0:
                if not already_non_zero_found:
                    continue
            already_non_zero_found = True
            output_list.append(entry)

        web_information = self._get_data()
        full_containers = self.cleanup(web_information)

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

        # [END solution_printer]

    def get_route(self):
        data = self.get_data()

        # Create the routing index manager.
        # [START index_manager]
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )
        # [END index_manager]

        # Create Routing Model.
        # [START routing_model]
        routing = pywrapcp.RoutingModel(manager)
        # [END routing_model]

        # Create and register a transit callback.
        # [START transit_callback]
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        # [END transit_callback]

        # Define cost of each arc.
        # [START arc_cost]
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        # [END arc_cost]

        # Add Capacity constraint.
        # [START capacity_constraint]
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
        # [END capacity_constraint]

        # Setting first solution heuristic.
        # [START parameters]
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(1)
        # [END parameters]

        # Solve the problem.
        # [START solve]
        solution = routing.SolveWithParameters(search_parameters)
        # [END solve]

        # Print solution on console.
        # [START print_solution]
        if solution:
            return self.get_solution(data, manager, routing, solution)
        # [END print_solution]


Route_planing()


# print(bergisch_gladbach_connect.get_fastest_time_in_seconds((50.991172, 7.123864),(50.9888253,7.104528)))
