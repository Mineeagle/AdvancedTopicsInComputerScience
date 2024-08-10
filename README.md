# AdvancedTopicsInComputerScience
This repo contains some stuff for a module in university. To be more precise, it contains the routeplanning code for the used clothing containers.

---

This repo is archived.

---

# Usage
Simply put, run the main.py file and the route will be generate and sent to a server. But please change the path in main.py which points to the config.json file.

Adjustments can be made in the [config.json](config.json) file. It may look like this:

```json
{
    "maps_link_sending_url": "https://altkleider.davidhojczyk.de/api/route/add",
    "container_information_url": "https://altkleider.davidhojczyk.de/api/container/list",
    "kippemuehle_lat": 50.982761,
    "kippemuehle_lon": 7.118816,
    "graph_file_path": "bergischGladbach.graphml",
    "dist": 5000,
    "simplify": false,
    "network_type": "drive",
    "central_lcoation_lat": 50.991172,
    "central_lcoation_lon": 7.123864,
    "regenerate_graph_file": false,
    "_comment": "Under here is just metadata and debugging stuff",
    "last_response": "<Response [200]>",
    "last_link": "https://www.google.com/maps/dir/?api=1&origin=50.982761,7.118816&waypoints=50.9847289,7.1223194|50.9842428,7.1089422|50.9827208,7.1096795|50.9838711,7.1192476|50.982761,7.118816|50.9798778,7.1189576|50.9762587,7.1213779|50.9843256,7.1261781&destination=50.982761,7.118816",
    "last_time_stamp": "2024-02-05 09:41:49.001462"
}
```

Using this config file, the code can be adapted to fit one's needs:
|           Field           | Contents                                                                                                  |
| ----------------------- | --------------------------------------------------------------------------------------------------------- |
|   maps_link_sending_url   | The url where the link will be sent to                                                                    |
| container_information_url | The url where the information about the container can be found                                            |
|      kippemuehle_lat      | Latitude of the starting point for the vehicle                                                            |
|      kippemuehle_lon      | Longitude of the starting point for the vehicle                                                           |
|      graph_file_path      | Path where a graph file will be saved to reuse it later                                                   |
|           dist            | Distance (in meters) around the central location; determines the size of the generated stree graph                     |
|         simplify          | Whether the generated Graph should be simplified, or stay accurate                                        |
|       network_type        | For home should the graph be generated; "drive" equals a car mode                                         |
|   central_lcoation_lat    | Latitude of the central location which is the center of the graph                                         |
|   central_lcoation_lon    | Longitude of the central location which is the center of the graph                                        |
|   regenerate_graph_file   | If set to true, the graph file will be regenerated the next run; value will be set to false automatically |
|         _comment          | Just a comment to seperate the two areas                                                                  |
|       last_response       | Last response from uploading the link to the server                                                       |
|         last_link         | The last generated link                                                                                   |
|      last_time_stamp      | Timestamp of the last link generation                                                                     |
