import networkx as nx
import pandas as pd
from common.paths import File
import re
import numpy as np

def return_linked_cases(x):

    if x is not np.nan:
        print('x is:', x)
        results = re.findall('\d+', x)
        if not results:
            return np.nan
        else:
            return results
    else:
        return np.nan



aggregated_cases = pd.read_csv(File.aggregated_cases_csv)

# Drop all columns except Case Number and Links
links_df = aggregated_cases[['Case Number', 'Links']]


links_df['List of Linked Cases'] = links_df['Links'].map(return_linked_cases)



G = nx.Graph()

list_of_edges = []


