import json
import re

from shapely.geometry import shape, Point

class CompareWithManualGraph:

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

    @staticmethod
    def get_polygon_array(directory):

        polygon_array = []

        with open(directory, 'r') as f:
            js = json.load(f)

        for feature in js['features']:


            properties = feature['properties']
            name = properties['Name']

            polygon = shape(feature['geometry'])

            polygon_array.append((name, polygon))

        return polygon_array


    @staticmethod
    def get_neighbouring_grcs(polygon_array, name_to_grc):

        neighbours = {}

        for p in polygon_array:

            name_of_p = name_to_grc[p[0]]

            polygon_of_p = p[1]

            neighbours_of_p = []

            for p2 in polygon_array:

                name_of_p2 = name_to_grc[p2[0]]

                polygon_of_p2 = p2[1]

                if polygon_of_p != polygon_of_p2 and polygon_of_p.intersects(polygon_of_p2):
                    neighbours_of_p.append(name_of_p2)

            neighbours[name_of_p] = neighbours_of_p


        return neighbours


path = '../grc files/eld2015.geojson'

name_to_grc = CompareWithManualGraph.get_name_to_grc_dictionary(path)

polygon_array = CompareWithManualGraph.get_polygon_array(path)

neighbouring_grcs = CompareWithManualGraph.get_neighbouring_grcs(polygon_array, name_to_grc)

print('')