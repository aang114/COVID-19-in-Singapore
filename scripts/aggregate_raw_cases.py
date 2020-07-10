import pandas as pd

from modules.aggregate import Aggergate

path = '../csv files/RAW_CASES.csv'
raw_cases_df = pd.read_csv(path)


cases_groupby = raw_cases_df.groupby('Case Number')

aggregated_cases_df = cases_groupby.agg(Aggergate.aggregate_linked_cases)

aggregated_cases_df.to_csv('../csv files/AGGREGATED.csv')

