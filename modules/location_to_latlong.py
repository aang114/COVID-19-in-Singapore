import googlemaps

class LocationToLatlong:

    def __init__(self, key):

        self.gmaps_key = googlemaps.Client(key=key)



    def get_latlong_from_location(self, location):

        geocode_result = self.gmaps_key.geocode(location, region='sg')

        lat = geocode_result[0]['geometry']['location']['lat']

        long = geocode_result[0]['geometry']['location']['lng']

        return (lat, long)



