from modules.scrape_moh_websites import *
from modules.convert_html_to_txt import *

scrapper = ScrapeMOHWebsites()

urls, dates = scrapper.get_all_cases()


scrapper.get_accuracy(dates)



#print(urls)

dates = [d.strftime('%d%m%Y') for d in dates]

#print('len(dates) is',len(dates))
#print('len(url) is',len(urls))

#urls = [urls[len(urls) - 5]]
#dates = [dates[len(dates) - 5]]

converter = ConvertHTMLToTxt()

converter.convert(urls, dates, "../text files/".replace(' ', '\ '))







