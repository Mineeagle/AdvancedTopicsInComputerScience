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
