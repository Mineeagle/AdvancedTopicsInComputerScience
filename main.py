from cleaned_route_planning import RoutePlanning
import requests
from link_sender import LinkSender
import json

def main():

    path = "/home/fawn/Root/dev/advanced_topics_in_cs/AdvancedTopicsInComputerScience/config.json"
    with open(path, "r") as json_file:
        config_dict = json.load(json_file)
    rp = RoutePlanning()
    link = rp.get_google_maps_link()
    print(LinkSender.send_link(config_dict, link))
    

if __name__ == "__main__":
    main()