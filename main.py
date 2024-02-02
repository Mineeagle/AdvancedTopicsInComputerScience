from cleaned_route_planning import RoutePlanning
import requests

def main():
    rp = RoutePlanning()
    link = rp.get_google_maps_link()
    print(requests.post(url=r"https://altkleider.davidhojczyk.de/api/route/add", json={"text":link}))

if __name__ == "__main__":
    main()