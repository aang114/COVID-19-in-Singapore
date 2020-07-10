import requests
from bs4 import BeautifulSoup

from datetime import datetime

import pandas as pd

import json

def return_desired_ancestor(element, str):

  #print("hello world")

  while element.name != str:
    element = element.parent

  return element

class ScrapeMOHWebsites:

    def get_all_cases(self):

        links_list = []

        dates_list = []

        url = "https://www.moh.gov.sg/covid-19/past-updates"

        source_code = requests.get(url)

        plain_text = source_code.text

        # plain_text

        soup = BeautifulSoup(plain_text)

        # for link in soup.findAll('a', {"title" : '', "target" : "_blank"}):

        for link in soup.findAll('a'):

            # print(link)

            href = link.get('href')

            # print(link.string)

            # if "cases-of-covid-19-infection" in href or "case-of-covid-19-infection" in href or "cases-of-covid19-infection" in href or "case-of-covid19-infection" in href:

            if "cases-of-covid-19-infection-confirmed" in href or "case-of-covid-19-infection-confirmed" in href or "cases-of-covid19-infection-confirmed" in href or "case-of-covid19-infection-confirmed" in href or "cases-of-novel-coronavirus-infection-confirmed" in href or "case-of-novel-coronavirus-infection-confirmed" in href:

                #print(href)

                links_list.append(href)

                # print("CONFIRMED")

                # print("parent tr is", return_desired_ancestor(link, 'tr'))

                tr = return_desired_ancestor(link, 'tr')

                dateCell = tr.find("span")

                try:
                    date = dateCell.string.strip()
                except:
                    links_list.pop()
                    continue

                date = datetime.strptime(date, '%d %b %Y')

                # print("datecell is", dateCell)

                #try:
                    #date = dateCell.string.strip()
                #except:
                    #date = ''

                #try:
                   #date = datetime.strptime(date, '%d %b %Y')
                #except:
                   #date = datetime.strptime('26 Jun 2022', '%d %b %Y')


                # print("date is", date)

                # exit()

                dates_list.append(date)

        return (links_list, dates_list)

    def get_accuracy(self, dates):

        print("my length is", len(dates))

        mini = min(dates)
        maxi = max(dates)

        print('mini is', mini)
        print('maxi is', maxi)

        notIn = []
        inside = []

        for d in pd.date_range(mini, maxi):


            if d in dates:

                inside.append(d)

            else:
                #print('i am not inside:',d)
                notIn.append(d)


        duplicate_dates = set([x for x in dates if dates.count(x) > 1])

        data = {}
        data['date'] = {

            'length_of_dates_inside': len(inside),

            'length_of_dates_not_inside': len(notIn),

            'minimum date': mini.strftime('%d%m%Y'),

            'maximum date': maxi.strftime('%d%m%Y'),

            'duplicate dates' : [d.strftime('%d%m%Y') for d in duplicate_dates],

            'notInside': [d.strftime('%d%m%Y') for d in notIn],

            'inside': [d.strftime('%d%m%Y') for d in inside],
        }


        string = json.dumps(data)

        with open('../log files/download_information.txt', 'w') as f:
            f.write(string)


