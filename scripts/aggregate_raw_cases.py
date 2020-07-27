import pandas as pd
from modules.aggregate import Aggergate
from common.paths import File

raw_cases_df = pd.read_csv(File.complete_raw_cases_csv)

cases_groupby = raw_cases_df.groupby('Case Number')

aggregated_cases_df = cases_groupby.agg(Aggergate.aggregate_linked_cases)

aggregated_cases_df.to_csv(File.aggregated_csv)

