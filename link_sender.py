import requests


class LinkSender:
    @staticmethod
    def send_link(data_dict, link):
        url = data_dict["maps_link_sending_url"]
        return requests.post(url, json={"link": link})
