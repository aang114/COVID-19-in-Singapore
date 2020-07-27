import pandas as pd
import numpy as np

from modules.location_to_latlong import *

from common.paths import File

from modules.log import Log

df = pd.read_csv(File.aggregated_csv, parse_dates=['Date of \nConfirmation'])

latlong_df = pd.DataFrame(data=None, columns=['Lattitude', 'Longitude'])

latlong_searcher = LocationToLatlong(key='AIzaSyAVEfTkmA0VG62RS-LEjhebpM6G7R1xUtU')

# create empty json file
open(File.failed_latlong_locations_json, 'w')

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

            Log.append_to_json_file(directory=File.failed_latlong_locations_json, key=cluster, value=str(e))


new_df = pd.concat([df, latlong_df], axis=1)

new_df.to_csv(File.aggregated_with_latlong_csv)