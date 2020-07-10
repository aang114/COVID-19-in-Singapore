import pandas as pd

from modules.aggregate import Aggergate

from modules.date import Date

import json

from modules.log import Log

from datetime import datetime as dt

# Create new Table that gives the Cases for every date

path = '../csv files/AGGREGATED_WITH_GRC.csv'

df = pd.read_csv(path, parse_dates=['Date of \nConfirmation'])

dfc = Aggergate.get_aggregated_dates_plus_grcs(df)

# Find Missing Dates

missing_dates = Date.find_missing_dates(dates_array=dfc.columns)

missing_dates_string = [d.strftime('%d%m%Y') for d in missing_dates]

with open('../log files/failed_dates.json') as f:
    date_to_error = json.load(f)

unscraped_dates_string = [d for d in missing_dates_string if date_to_error.get(d) == Log.ParseTextFileError.DATE_DOES_NOT_MATCH
                or date_to_error.get(d) == Log.ParseTextFileError.REGEX_CRASHED or date_to_error.get(d) == Log.ParseTextFileError.NO_WEBLINK_FOUND]

dates_to_add_string = set(missing_dates_string) - set(unscraped_dates_string)

dates_to_add = [dt.strptime(d, '%d%m%Y') for d in dates_to_add_string]

dates_to_add_df = pd.DataFrame(data=None, columns=dates_to_add)

dfc =  pd.concat([dfc, dates_to_add_df])

dfc = dfc.fillna(value=0)


# Add Missing GRCs

path = '../csv files/NUMBER_OF_CASES.csv'

dfc.to_csv(path)

input_matrix = Aggergate.add_missing_grc_rows(dfc)

input_matrix = input_matrix.cumsum(axis=1)

path = '../csv files/INPUT_MATRIX.csv'

input_matrix.to_csv(path)
