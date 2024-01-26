import osmnx as ox
import networkx as nx


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

    def get_fastest_route(self, origin_coordinates, destination_coordinates):
        """
        Returns the graph nodes of the fastest route.
        """
        origin_node = self._convert_coordinates_to_node(origin_coordinates)
        destination_node = self._convert_coordinates_to_node(destination_coordinates)
        return ox.shortest_path(
            self.graph, origin_node, destination_node, weigth="travel_time"
        )

    def get_shortest_route(self, origin_coordinates, destination_coordinates):
        """
        Returns the graph nodes of the shortest route.
        """
        origin_node = self._convert_coordinates_to_node(origin_coordinates)
        destination_node = self._convert_coordinates_to_node(destination_coordinates)
        return ox.shortest_path(
            self.graph, origin_node, destination_node, weigth="length"
        )

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
