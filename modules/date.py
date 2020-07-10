import pandas as pd

class Date:

    @staticmethod
    def find_missing_dates(dates_array):

        minimum = min(dates_array)
        maximum = max(dates_array)

        missing = []

        for d in pd.date_range(minimum, maximum):

            if d not in dates_array:
                missing.append(d)


        return missing

