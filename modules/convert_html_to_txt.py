import os
import json


class ConvertHTMLToTxt:

    def convert(self, links, dates, path):

        inside = []

        notIn = []

        for i, link in enumerate(links):



            try:
                os.system("lynx -width=10000000 --dump " + link + " > " + path + dates[i])
                inside.append(link)
            except:
                notIn.append(link)


        self.save_information(inside, notIn, links)

    def save_information(self, inside, notIn, links):

        duplicate_links = list(set([x for x in links if links.count(x) > 1]))

        data = {}
        data['date'] = {

            'length_of_links_inside': len(inside),

            'length_of_links_not_inside': len(notIn),

            'duplicate links' : duplicate_links,

            'notInside': notIn,

            'inside': inside,
        }

        string = json.dumps(data)

        with open('../log files/links_information.txt', 'w') as f:
            f.write(string)






