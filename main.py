from cleaned_route_planning import RoutePlanning
import requests
from link_sender import LinkSender
import json
import datetime
import os


def main():

    PATH = "/home/fawn/Root/dev/advanced_topics_in_cs/AdvancedTopicsInComputerScience/config.json"
    with open(PATH, "r") as json_file:
        config_dict = json.load(json_file)

    if config_dict["regenerate_graph_file"]:
        config_dict["regenerate_graph_file"] = False
        if os.path.exists(config_dict["graph_file_path"]):
            os.remove(config_dict["graph_file_path"])

    rp = RoutePlanning(config_dict)
    link = rp.get_google_maps_link()
    config_dict["last_response"] = str(LinkSender.send_link(config_dict, link))
    config_dict["last_link"] = link
    config_dict["last_time_stamp"] = str(datetime.datetime.now())

    with open(PATH, "w") as json_file:
        json.dump(config_dict, json_file, indent=4)


if __name__ == "__main__":
    main()
