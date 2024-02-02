from cleaned_route_planning import RoutePlanning
import requests
from link_sender import LinkSender
import json


def main():

    PATH = "/home/fawn/Root/dev/advanced_topics_in_cs/AdvancedTopicsInComputerScience/config.json"
    with open(PATH, "r") as json_file:
        config_dict = json.load(json_file)

    rp = RoutePlanning(config_dict)
    link = rp.get_google_maps_link()
    config_dict["last_response"] = str(LinkSender.send_link(config_dict, link))
    config_dict["last_link"] = link

    with open(PATH, "w") as json_file:
        json.dump(config_dict, json_file, indent=4)


if __name__ == "__main__":
    main()
