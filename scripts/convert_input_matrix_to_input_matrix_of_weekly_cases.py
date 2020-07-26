from common.paths import File
import pandas as pd

import numpy as np

def get_week_numbers_with_7_days(week_numbers_list : list):

    week_numbers_with_7_days = []
    week_numbers_set = set(week_numbers_list)

    for wn in week_numbers_set:
        if week_numbers_list.count(wn) == 7:
            week_numbers_with_7_days.append(wn)

    return week_numbers_with_7_days

def replace_missing_week_numbers_with_nan(week_numbers : list, week_numbers_with_7_days : list):
    for index, wn in enumerate(week_numbers):
        if wn not in week_numbers_with_7_days:
            week_numbers[index] = np.nan

    return week_numbers

input_matrix = pd.read_csv(File.input_matrix, index_col=0)
input_matrix.columns = pd.to_datetime(input_matrix.columns)

week_numbers = input_matrix.columns.strftime('%W').values.tolist()
week_numbers_with_7_days = get_week_numbers_with_7_days(week_numbers)
new_column = replace_missing_week_numbers_with_nan(week_numbers=week_numbers, week_numbers_with_7_days=week_numbers_with_7_days)

input_matrix.columns = new_column

# Create Number of Weekly Cases CSV
input_matrix.to_csv(File.number_of_weekly_cases_csv)

input_matrix_of_weekly_cases = input_matrix.groupby(input_matrix.columns, axis=1).sum()

# Create Input Matrix of Weekly Cases CSV
input_matrix_of_weekly_cases.to_csv(File.input_matrix_of_weekly_cases)

