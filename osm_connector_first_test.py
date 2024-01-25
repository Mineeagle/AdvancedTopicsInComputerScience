import osmnx as ox
import networkx as nx

# coordinates: (lat, lng)
LOCATION_COORDINATES = (50.984865, 7.121218) # near McDonald's in Bergisch Gladbach
ORIGIN_COORDINATES = (50.983979, 7.119159) # near FHDW
DEST_COORDINATES = (50.988673, 7.121047) # near dance school
GRAPH_FILE_PATH = "mcdonalds_map.graphml"

# Define the general area / location where the destination and goal are situated
# dist => area in meters around the location
# simplify => accuracy of the graph
# network_type => mode of transportation (eg. "drive" for driving)
G = ox.graph_from_point(LOCATION_COORDINATES, dist=3000, simplify=True, network_type="drive")

# OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# load a pregenerated graph, or save the graph for later use
try:
    G = ox.load_graphml(GRAPH_FILE_PATH)
except FileNotFoundError:
    ox.save_graphml(G, GRAPH_FILE_PATH)

# convert input coordinates into nodes
origin_node = ox.nearest_nodes(G, Y=ORIGIN_COORDINATES[0], X=ORIGIN_COORDINATES[1])
destination_node = ox.nearest_nodes(G, Y=DEST_COORDINATES[0], X=DEST_COORDINATES[1])

# shortest route by time
shortest_route_by_travel_time = ox.shortest_path(G, origin_node, destination_node, weight='travel_time')
travel_time_in_seconds = nx.shortest_path_length(G, origin_node, destination_node, weight='travel_time')
print(f"Duration of the route in seconds: {travel_time_in_seconds}")

# shortes route by distance
shortest_route_by_distance = ox.shortest_path(G, origin_node, destination_node, weight='length')
distance_in_meters = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
print(f"This is the length of the route in meters: {distance_in_meters}")
