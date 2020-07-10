import pandas as pd

import numpy as np

import re

from datetime import datetime as dt

from modules.latlong_to_grc import LatlongToGRC

from modules.log import Log

class Aggergate:


    @staticmethod
    def add_missing_grc_rows(df):

        new_df = df

        path = '../grc files/eld2015.geojson'

        name_to_grc = LatlongToGRC.get_name_to_grc_dictionary(path)

        for grc in name_to_grc.values():

            if grc not in df.index:
                new_df = new_df.append(pd.Series(name=grc))


        new_df = new_df.fillna(0)

        return new_df



    @staticmethod
    def get_aggregated_dates_plus_grcs(df):

        groupby = df.groupby(['GRC', 'Date of \nConfirmation'])

        aggregated_df = groupby.size().to_frame('Number of Cases')

        aggregated_df['GRC'] = aggregated_df.index.get_level_values('GRC')
        aggregated_df['Date'] = aggregated_df.index.get_level_values('Date of \nConfirmation')
        aggregated_df.reset_index(drop=True, inplace=True)
        aggregated_df = aggregated_df.pivot(index="GRC", columns="Date", values='Number of Cases')
        aggregated_df = aggregated_df.fillna(0)

        return aggregated_df



    @staticmethod
    def parse_date(date_string):

        search = re.search('^\d+ [A-Za-z][A-Za-z][A-Za-z]', date_string)

        #print('search is:', search)

        if search:
            trimmed_date_string = search.group(0) + ' 2020'

            date = dt.strptime(trimmed_date_string, '%d %b %Y')

        else:
            raise ValueError('COULD NOT PARSE DATE:', date_string)

        return date



    @staticmethod
    def __get_minimum_date_string(series):

        filtered_series_of_dates = series[series.isnull() == False]

        dates_array = [Aggergate.parse_date(date_string) for date_string in filtered_series_of_dates.values]

        minimum = min(dates_array)

        return minimum

    @staticmethod
    def __join_all_linked_cases(series):
        filtered_series_of_links_array = series[series.isnull() == False]
        return filtered_series_of_links_array.values

    @staticmethod
    def aggregate_linked_cases(series):

        # if there is any 'False' in series.isnull()
        if (series.isnull() == False).any():

            if series.name == 'Links':

                try:
                    all_linked_cases = Aggergate.__join_all_linked_cases(series)
                    return all_linked_cases
                except:
                    #print('WAS NOT ABLE TO JOIN')
                    pass

            elif series.name == 'Date of \nConfirmation':

                try:
                    # print(' NOT WORK FOR SERIES:', series)
                    return Aggergate.__get_minimum_date_string(series)
                except:
                    #print('DID NOT WORK FOR SERIES:', series.values)

                    #filtered_series = series[series.isnull() == False]
                    #return filtered_series.values[0]

                    dir = '../log files/unparsed_dates.json'

                    for date in series:
                        Log.append_to_json_file(directory=dir, key=date, value='Could Not Parse')


                    return np.nan


            else:

                try:
                    filtered_series = series[series.isnull() == False]
                    return filtered_series.values[0]
                except:
                    print('IT DIDNT WORK FOR COLUMN:', series.name)


        else:
            return np.nan
