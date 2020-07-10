import json
from json.decoder import JSONDecodeError


class Log:

    class ParseTextFileError:
        NO_WEBLINK_FOUND = 'A very specific bad thing happened. (NO LINK FOUND!!!!)'
        DATE_DOES_NOT_MATCH = 'A very specific bad thing happened. (DATE DOES NOT MATCH)'
        REGEX_CRASHED = "'NoneType' object has no attribute 'group'"


    @staticmethod
    def append_to_json_file(directory, key, value):

        try:

            with open(directory) as f:
                try:
                    dic = json.load(f)
                except JSONDecodeError:
                    dic = {}

        except:
            dic = {}

        dic[key] = value

        with open(directory, 'w') as f:
            json.dump(obj=dic, fp=f)