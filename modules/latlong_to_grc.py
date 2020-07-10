import re

import json

# depending on your version, use: from shapely.geometry import shape, Point
from shapely.geometry import shape, Point

class LatlongToGRC:

    def __init__(self, directory):
        self.directory = directory

        self.name_to_grc = LatlongToGRC.get_name_to_grc_dictionary(directory)


    @staticmethod
    def get_name_to_grc_dictionary(directory):

        name_to_grc = {}

        # example directory: eld2015.geojson (can end with geojson - tested with ipython!)
        with open(directory, 'r') as f:
            js = json.load(f)

        for feature in js['features']:

            properties = feature['properties']

            name = properties['Name']

            description = properties['Description']

            grc = re.search('<th>ED_DESC</th> <td>(.+?)</td>', description).group(1)

            name_to_grc[name] = grc


        return name_to_grc



    def get_grc_from_latlong(self, latlong):

        lat = latlong[0]
        long = latlong[1]



        # load GeoJSON file containing sectors
        with open(self.directory, 'r') as f:
            js = json.load(f)

        # construct point based on lon/lat returned by geocoder
        point = Point(long, lat)

        #print('point is:', point)

        # check each polygon to see if it contains the point
        for feature in js['features']:

            polygon = shape(feature['geometry'])

            #print('polygon is:', polygon)

            if polygon.contains(point):
                #print('I AM ALIVE!!!')


                properties = feature['properties']
                name = properties['Name']

                return self.name_to_grc[name]
            else:
                print(end='')


        raise ValueError('NO GRC MATCHED! - WAHH LANNN EEE')



