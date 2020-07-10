from modules.convert_html_to_txt import *
from modules.parse_text_file import *

from datetime import datetime as dt

from modules.log import Log

def log_exception(e, date, file_cleared=False):

    if file_cleared is False:
        open('../log files/failed_dates.json', 'w').close()
        open('../log files/text_files_scraping_information.txt', 'w').close()
        log_exception.__defaults__ = (True,)

    dir = '../log files/failed_dates.json'
    Log.append_to_json_file(directory=dir, key=date, value=str(e))


    with open('../log files/text_files_scraping_information.txt', 'a') as file:
        text = 'Date: ' + date + '\n' + 'Reason:' + str(e) + '\n\n'
        file.write(text)



cases_df_array = []
locations_visited_df_array = []

for date in os.listdir("../text files/"):

    if not date.startswith('.'):
        date_dt = dt.strptime(date, '%d%m%Y')
        parser = ParseTextFile("../text files/" + date, date_dt)

        try:
            df_array = parser.get_data_frames()

            for df in df_array:

                if 'Case Number' in df.columns:
                    cases_df_array.append(df)
                else:
                    locations_visited_df_array.append(df)

        except Exception as e:
            log_exception(e, date)





cases_df = pd.concat(cases_df_array)
cases_df.to_csv('../csv files/RAW_CASES.csv')