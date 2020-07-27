import pandas as pd
import numpy as np

from modules.latlong_to_grc import *

from common.paths import File

df = pd.read_csv(File.aggregated_with_latlong_csv, parse_dates=['Date of \nConfirmation'])

grc_df = pd.DataFrame(columns=['GRC'])

path = '../grc files/eld2015.geojson'

grc_searcher = LatlongToGRC(path)

for (lat, long) in zip(df['Lattitude'], df['Longitude']):

    if pd.isnull(lat) or pd.isnull(long):
        grc = np.nan

        row_to_add = pd.DataFrame([[grc]], columns=grc_df.columns)
        grc_df = grc_df.append(row_to_add, ignore_index=True)

    else:
        try:
            grc = grc_searcher.get_grc_from_latlong((lat, long))

            row_to_add = pd.DataFrame([[grc]], columns=grc_df.columns)
            grc_df = grc_df.append(row_to_add, ignore_index=True)

        except Exception as e:
            print('Crashed')
            print('Reason:', e)


new_df = pd.concat([df, grc_df], axis=1)

new_df.to_csv(File.aggregated_with_grc_csv)