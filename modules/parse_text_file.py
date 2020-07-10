import pandas as pd
import re

import camelot

import ssl

from modules import helper_methods


class ParseTextFile:

    def __init__(self, directory, date):

        self.directory = directory

        self.date = date


    def verify_date_or_fail(self, date, text):

        day = int(date.strftime('%d'))

        #date_string_with_suffix = date.strftime('%d' + helper_methods.get_day_suffix(day) + ' %b %Y')

        date_string_with_suffix_without_zero_padding = date.strftime(str(day) + helper_methods.get_day_suffix(day) + ' %b %Y')

        regex =  date_string_with_suffix_without_zero_padding + '\n'

        if re.search(regex, text):
            return
        else:
            #print("THANK YOU:", date_string_with_suffix_without_zero_padding)
            raise ValueError('A very specific bad thing happened. (DATE DOES NOT MATCH)')



    def get_data_frames(self):

        f = open(self.directory, 'r', encoding='unicode_escape')

        text = f.read()

        self.verify_date_or_fail(self.date, text)

        if 'Annex' in text:

            annex_url = self.get_pdf_url(text)

            return self.scan_pdf(annex_url)

        else:
            return self.scan_lines(self.directory)



    def scan_lines(self, directory):

        f = open(directory, 'r', encoding='unicode_escape')

        text = f.read()

        new_cases_df_tuple = self.get_new_cases(text)

        clusters_df_tuple = self.get_cluster_links(text)

        #links_df_tuple = self.get_links_between_cases(text)

        #return new_cases_df_tuple + clusters_df_tuple + links_df_tuple

        return new_cases_df_tuple + clusters_df_tuple


    def get_pdf_url(self, text):

        annex_c = '\[' + '(\d+)' + '\]' + 'Annex C'

        annex_c_one_space_only = '\[' + '(\d+)' + '\]' + '[\s\S]' + 'Annex C'

        annex_no_alphabet = '\[' + '(\d+)' + '\]' + 'Annex for'

        annex_no_alphabet_one_space_only = '\[' + '(\d+)' + '\]' + '[\s\S]' + 'Annex for'

        additional_X_cases_of_COVID = '\[(\d+)\]additional \d+ cases of COVID-19 infection'

        regex = '(' + '?:' + annex_c + '|' + annex_c_one_space_only + '|' + annex_no_alphabet + '|' + annex_no_alphabet_one_space_only + '|' + additional_X_cases_of_COVID + ')'

        annex_search = re.search(regex, text)

        annex_number = ''

        if annex_search is None:
            annex_b = '\[' + '(\d+)' + '\]' + 'Annex B'
            annex_b_one_space_only = '\[' + '(\d+)' + '\]' + '[\s\S]' + 'Annex B'
            regex = '(' + '?:' + annex_b + '|' + annex_b_one_space_only + ')'
            annex_search = re.search(regex, text)

        if not annex_search:
            raise ValueError('A very specific bad thing happened. (NO LINK FOUND!!!!)')

        for string in annex_search.groups():
            if string:
                annex_number = string
                break



        references_description = re.search('References\n([\s\S]+)', text).group(1)

        get_url_regex = annex_number + '\.' + '([\s\S]+)' + str(int(annex_number) + 1) + '\.'

        url = re.search(get_url_regex, references_description).group(1)

        url = url.replace('\n', '')

        url = url.strip()

        return url

    def get_df_with_corrected_column_labels(self, df, recurse=True):

        boolean_mask = [ True if 'Case Number' in x and 'Date of \nConfirmation' in x
                                else False for x in df.values ]

        #boolean_mask = [True if 'Case Number' in x else False for x in df.values]

        # row number = index (same thing)
        matching_row_numbers = df.index[boolean_mask]


        if len(matching_row_numbers) > 1:
            raise ValueError('THERE IS MORE THAN ONE ROW/COLUMN WITH "CASE NUMBER" AND "Date of \nConfirmation"')

        elif len(matching_row_numbers) == 1:

            row_number = matching_row_numbers.values[0]

            df.columns = df.iloc[row_number]

            df = df.drop(df.index[row_number])

            return df

        else:
            if recurse:

                return self.get_df_with_corrected_column_labels(df.T, recurse=False)

            else:
                raise ValueError('NO ROW/COLUMN WITH "Date of \nConfirmation" AND "CASE NUMBER" FOUND')





    def scan_pdf(self, url):

        ssl._create_default_https_context = ssl._create_unverified_context

        try:
            tables = camelot.read_pdf(url, pages='all', split_text=True)
        except:
            tables = camelot.read_pdf(url, pages='all')

        #print('tables is', tables)

        df_array = []

        for table in tables:

            # HOW IT WAS DONE BEFORE;
            #df = table.df
            #df.columns = df.iloc[0]
            #df = df.drop(df.index[0])
            #df_array.append(df)


            # HOW IT IS DONE NOW

            df = table.df

            try:
                df = self.get_df_with_corrected_column_labels(df)
                df_array.append(df)
            except:
                pass



        return tuple([df for df in df_array if df.empty == False])


    def get_regex_for_finding_links(self):

        links_header = 'Links between previous cases found\n'

        about_confirmed_cases_header = "   About the confirmed cases\n"

        cases_from_public_sector_header = '   Cases from public healthcare sector\n'

        # This will only be triggered if about_confirmed_cases_header and cases_from_public_sector_header doesn't exist
        ministry_of_health_header = 'Ministry of Health\n'

        regex = links_header + '([\s\S]+)' + '(?=' + about_confirmed_cases_header + '|' + cases_from_public_sector_header + '|' + ministry_of_health_header + ')'

        return regex

    def get_cluster_links(self, text):

        regex = self.get_regex_for_finding_links()

        links_description = re.search(regex, text).group(1)

        #links_description = re.search("Links between previous cases found\n([\s\S]+)About the confirmed cases\n",
        #                              text).group(1)



        df1 = self.get_cluster_links_MANY_CASES(links_description)

        df2 = self.get_cluster_links_ONE_CASE_ONLY(links_description)

        df_array = [df1, df2]

        return tuple([df for df in df_array if df.empty == False])


    def get_cluster_links_MANY_CASES(self, links_description):

        df = pd.DataFrame(data=None, columns=['Case Number', 'Cluster'])

        many_cases = '(?:Cases \d+)'

        last_case = '(?:and \d+)'

        regex_with_and = '(' + many_cases + '[^.]+?' + last_case + ')' + '[^.]+?' + 'linked to ' + '(?!Case|Cases)' + '(' + '[^.]+?' + ')' + '\.'

        for cases_description, cluster in re.findall(regex_with_and, links_description):

            cases = [int(c) for c in re.findall('\d+', cases_description)]

            for case in cases:

                row_to_add = pd.DataFrame([[case, cluster]], columns=df.columns)

                df = df.append(row_to_add, ignore_index=True)


        return df


    def get_cluster_links_ONE_CASE_ONLY(self, links_description):

        df = pd.DataFrame(data=None, columns=['Case Number', 'Cluster'])

        one_case_only = '(?:Case \d+)'

        regex_without_and = '(' + one_case_only + ')' + '[^.]+?' + 'linked to ' + '(?!Case|Cases)' + '(' + '[^.]+?' + ')' + '\.'

        for case_description, cluster in re.findall(regex_without_and, links_description):

            case = re.search('\d+', case_description).group(0)

            row_to_add = pd.DataFrame([[case, cluster]], columns=df.columns)

            df = df.append(row_to_add, ignore_index=True)


        return df



    def get_links_between_cases(self, text):

        regex = self.get_regex_for_finding_links()

        links_description = re.search(regex, text).group(1)

        #links_description = re.search("Links between previous cases found\n([\s\S]+)About the confirmed cases\n",
        #                              text).group(1)

        df1 = self.get_links_between_cases_MANY_CASES(links_description)

        df2 = self.get_links_between_cases_ONE_CASE_ONLY(links_description)

        df_array = [df1, df2]

        return tuple([df for df in df_array if df.empty == False])


    def get_links_between_cases_MANY_CASES(self, links_description):

        df = pd.DataFrame(data=None, columns=['Case Number', 'Links'])

        many_cases = '(?:Cases \d+)'

        last_case = '(?:and \d+)'

        regex_with_and = '(' + many_cases + '[^.]+?' + last_case + ')' + '[^.]+?' + 'linked to ' + '(?=Case|Cases)' + '(' + '[^.]+?' + ')' + '\.'

        for cases_description, linked_cases_description in re.findall(regex_with_and, links_description):

            cases = [int(c) for c in re.findall('\d+', cases_description)]

            linked_cases = [int(c) for c in re.findall('\d+', linked_cases_description)]

            for case in cases:

                copy = linked_cases.copy()

                if case in copy:
                    copy.remove(case)

                row_to_add = pd.DataFrame([[case, copy]], columns=df.columns)

                df = df.append(row_to_add, ignore_index=True)


        return df


    def get_links_between_cases_ONE_CASE_ONLY(self, links_description):

        df = pd.DataFrame(data=None, columns=['Case Number', 'Links'])

        one_case_only = '(?:Case \d+)'

        regex_without_and = '(' + one_case_only + ')' + '[^.]+?' + 'linked to ' + '(?=Case|Cases)' + '(' + '[^.]+?' + ')' + '\.'

        for case_description, linked_cases_description in re.findall(regex_without_and, links_description):

            case = re.search('\d+', case_description).group(0)

            linked_cases = [int(c) for c in re.findall('\d+', linked_cases_description)]

            row_to_add = pd.DataFrame([[case, linked_cases]], columns=df.columns)

            df = df.append(row_to_add, ignore_index=True)


        return df


    def get_new_cases(self, text):

        df = pd.DataFrame(data=None, columns=['Case Number', 'Age (years)', 'Gender', 'Nationality', 'Key Places \nVisited after \nSymptoms \nOnset/ Swab (for \nasymptomatic \ncases)', 'Date of \nConfirmation'])

        bullet_start = '     \* Case \d+:'

        normal_start = '(?:' + '   Case \d+\n' + '|' + '   Case \d+ \(Announced on \d+ [a-zA-Z]+\)\n' + ')'

        bullet_or_normal_start = '(?:' + bullet_start + '|' + normal_start + ')'

        update = 'Update on condition of confirmed cases\n'

        bullet_or_normal_start_or_update = '(?:' + bullet_start + '|' + normal_start + '|' + update + ')'

        regex = bullet_or_normal_start + '[\s\S]*?' + '(?=' + bullet_or_normal_start_or_update + ')'

        for case_description in re.findall(regex, text):

            case_number = int(re.search("Case (\d+)", case_description).group(1))

            # case_number = string_to_number(case_number_string)

            age = re.search(" ([a-z0-9]+)[\-\s]year-old", case_description).group(1)

            try:
                age = int(age)
            except:
                age = helper_methods.text2int(age)

            try:
                gender = re.search(" (male|female) ", case_description).group(1)
            except:
                gender = None


            citizenship_match = re.search('(Singapore Citizen)' + '|' + '(Singapore citizen)' + '|' + '(Singaporean Citizen)' + '|' + '(Singaporean citizen)' +  '|' + '(Permanent Resident)' + '|' + '([A-Z].+? national)', case_description)

            for string in citizenship_match.groups():
                if string:
                    citizenship = string
                    break

            try:
                locations_description = re.search('Prior to hospital admission' + '([\s\S]+)', case_description).group(
                    1)
                locations = re.findall(' at (.+?)[,\.]', locations_description)
            except:
                locations = []

            date = self.date.strftime('%d %b')

            row_to_add = pd.DataFrame([[case_number, age, gender, citizenship, locations, date]], columns=df.columns)

            df = df.append(row_to_add, ignore_index=True)


        if df.empty:
            return ()
        else:
            return tuple([df])


#c = ParseTextFile('59')
