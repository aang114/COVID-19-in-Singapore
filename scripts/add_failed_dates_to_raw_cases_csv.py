from common.paths import File, Folder
import json
from modules.convert_html_to_txt import ConvertHTMLToTxt
import os
from datetime import datetime as dt
from modules.parse_text_file import ParseTextFile
import pandas as pd
from modules.log import Log

with open (File.url_of_failed_dates_json, 'r') as f:
    failed_dates_to_urls = json.load(f)

failed_dates = list(failed_dates_to_urls.keys())
urls = list(failed_dates_to_urls.values())

converter = ConvertHTMLToTxt()
converter.convert(urls, failed_dates, Folder.text_files_folder_for_failed_dates.replace(' ', '\ '))


missing_cases_df_array = []

newly_parsed_dates = []

for date in os.listdir(Folder.text_files_folder_for_failed_dates):
    if not date.startswith('.'):
        date_dt = dt.strptime(date, '%d%m%Y')
        parser = ParseTextFile(Folder.text_files_folder_for_failed_dates + date, date_dt)

        try:

            print('before')
            df_array = parser.get_data_frames()
            print('after')

            newly_parsed_dates.append(date)

            for df in df_array:
                if 'Case Number' in df.columns:
                    missing_cases_df_array.append(df)

        except Exception as e:
            pass


with open(File.failed_dates_json) as f:
    failed_dates_to_error = json.load(f)

with open(File.remaining_failed_dates_json, 'w') as f:
    for date in newly_parsed_dates:
        failed_dates_to_error.pop(date, None)

    json.dump(obj=failed_dates_to_error,fp=f)



missing_cases_df = pd.concat(missing_cases_df_array)

raw_cases_df = pd.read_csv(File.raw_cases_csv)

complete_raw_cases_df = pd.concat([missing_cases_df, raw_cases_df])

complete_raw_cases_df.to_csv(File.complete_raw_cases_csv)







