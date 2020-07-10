import pandas as pd
import numpy as np

from modules.location_to_latlong import *

from modules.latlong_to_grc import *

path = '../csv files/AGGREGATED.csv'

df = pd.read_csv(path, parse_dates=['Date of \nConfirmation'])

latlong_df = pd.DataFrame(data=None, columns=['Lattitude', 'Longitude'])

latlong_searcher = LocationToLatlong(key='AIzaSyCNPJfnJra5qHyjv9Loc87UD_n6qL09YmE')

for cluster in df['Cluster']:

    if pd.isnull(cluster):
        row_to_add = pd.DataFrame([[np.nan, np.nan]], columns=latlong_df.columns)
        latlong_df = latlong_df.append(row_to_add, ignore_index=True)
    else:
        try:
            latlong = latlong_searcher.get_latlong_from_location(cluster)

            lat = latlong[0]
            long = latlong[1]

            row_to_add = pd.DataFrame([[lat, long]], columns=latlong_df.columns)
            latlong_df = latlong_df.append(row_to_add, ignore_index=True)

        except Exception as e:
            print('crashed')
            row_to_add = pd.DataFrame([[np.nan, np.nan]], columns=latlong_df.columns)
            latlong_df = latlong_df.append(row_to_add, ignore_index=True)




new_df = pd.concat([df, latlong_df], axis=1)

path = '../csv files/AGGREGATED_WITH_LATLONG.csv'

new_df.to_csv(path)