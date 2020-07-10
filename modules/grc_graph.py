import json

import networkx as nx

class GRCGraph:

    @staticmethod
    def get_grc_to_neighbours(directory):

        with open(directory, 'r') as f:
            grc_to_neighbours = json.load(f)


        return grc_to_neighbours


    @staticmethod
    def create_graph_from_neighbours(grc_to_neighbours_dictionary):

        G = nx.Graph()

        list_of_edges = []

        for grc, neighbours in grc_to_neighbours_dictionary.items():

            for n in neighbours:
                edge = (grc, n)

                list_of_edges.append(edge)


        G.add_edges_from(list_of_edges)

        return G


