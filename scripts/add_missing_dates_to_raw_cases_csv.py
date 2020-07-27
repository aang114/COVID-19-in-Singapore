from common.paths import File, Folder
import json
from modules.convert_html_to_txt import ConvertHTMLToTxt

with open (File.url_of_failed_dates_json, 'r') as f:
    failed_dates_to_urls = json.load(f)

failed_dates = list(failed_dates_to_urls.keys())
urls = list(failed_dates_to_urls.values())

converter = ConvertHTMLToTxt()
converter.convert(urls, failed_dates, Folder.text_files_folder_for_failed_dates)







