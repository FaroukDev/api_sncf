from pprint import pprint
import json
import requests
import csv
import logging
import datetime


logging.basicConfig(filename='data.log', level=logging.DEBUG)
logging.info("Script started")

url = "https://api.sncf.com/v1/coverage/sncf/stop_areas"
headers = {"Authorization": "6df7dc97-1bdc-4539-af03-9d854dd236fe"}

def read_json(self):  # read and saves json
    response = requests.get(self.url, headers=self.headers)  # pop up for password
    # raw_data = json.loads(response.text) #dict
    with open('stop_areas.json', mode="w") as file:
        json.dump(response.text, file)
    # returns nothing, saves json

response = requests.get(url, headers=headers)  # pop up for password
raw_data = json.loads(response.text)


areas = raw_data["stop_areas"]  # list


logging.info("find name and id in areas")



def fetchnameandid():
    list_ids = []
    list_name = []
    for loop_area, loop_name in zip(areas, areas):
        if type(loop_area) == dict and type(loop_name) == dict:
            if "id" in loop_area.keys() and "name" in loop_name.keys():  # !!!!!!
                local_id = loop_area["id"]
                local_name = loop_name["name"]
                list_ids.append(local_id)
                list_name.append(local_name)
            else:
                print("Missing key id")
        else:
            print(f"Unexpected format {type(loop_area)}")
    return list_ids, list_name
fetchnameandid()

'''
how to find url 
'''
logging.info("find url in areas json file")


def findurl():
    list_link = []
    for loop_link in areas:
        if type(loop_link) == dict:
            if "links" in loop_link.keys():
                local_link = loop_link["links"]
                list_link.append(local_link)
            else:
                print("missing key links")
        else:
            print(f"Unexpected format {type(loop_link)}")
    return list_link
findurl()


'''
transform in csv file
'''
logging.info("transform file in csv")


def transform_in_csv():
    fname = "data.csv"
    with open(fname, 'w') as csv_file:
        csv_file = csv.writer(csv_file)
        csv_file.writerow(["id", "name"])
        for item in areas:
            return  csv_file.writerow([item['id'], item['name']])

transform_in_csv()
'''
how to find name
'''


def findname():
    list_name = []
    for loop_name in areas:
        if type(loop_name) == dict:
            if "name" in loop_name.keys():
                local_name = loop_name["name"]
                list_name.append(local_name)
            else:
                print("missing key name")
        else:
            print(f"Unexpected format {type(loop_name)}")
    return list_name
findname()


logging.info("fetch data info between paris and lyon")
'''
fetch journey between paris and lyon
'''
paris = "stop_area:OCE:SA:87686006"

lyon = "stop_area:OCE:SA:87722025"

URL = f"https://api.sncf.com/v1/journeys?from={paris}&to={lyon}"

headers = {"Authorization": "6df7dc97-1bdc-4539-af03-9d854dd236fe"}
req = requests.get(URL, headers=headers)

raw_data = req.json()

for data in raw_data["journeys"]:
    print(data)

'''
number of stop areas between paris and lyon
'''
#print(len(raw_data['journeys'][0]['sections'][1]['stop_date_times']))

logging.info("fetch number of stop areas between paris and lyon")
# for data in raw_data["journeys"]:
# print(len(data))

'''
Combien de temps d'arrêts entre chacunes d'elles
'''
logging.info("how long does each stop have")

stop_data = req.json()

#list_between_eight_and_twenty = []

logging.info("fetch number of tgv between 18H 20H00")
'''
combien de tgv partent entre 18H00 et 200H00

'''

my_tgv1 = raw_data["journeys"][0]["sections"][1]["stop_date_times"][3]["base_departure_date_time"]
my_tgv2 = raw_data["journeys"][0]["sections"][1]["stop_date_times"][2]["base_departure_date_time"]
print(my_tgv1, my_tgv2)

date1 = datetime.datetime.strptime('30-01-2021T18:09:03.283Z', '%d-%m-%YT%H:%M:%S.%fZ')
date2 = datetime.datetime.strptime('30-01-2021T18:10:00.283Z', '%d-%m-%YT%H:%M:%S.%fZ')
print(date1, date2)
logging.info("script_ended")
