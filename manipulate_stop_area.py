from pprint import pprint
import json
import requests
import csv
import logging


class main:
    logging.basicConfig(filename='data.log', level=logging.DEBUG)
    logging.info("Script started")

    url = "https://api.sncf.com/v1/coverage/sncf/stop_areas"
    headers = {"Authorization": "6df7dc97-1bdc-4539-af03-9d854dd236fe"}

    def read_json(self, url, headers):  # read and saves json
        response = requests.get(url, headers=headers)  # pop up for password
        # raw_data = json.loads(response.text) #dict
        with open('stop_areas.json', mode="w") as file:
            json.dump(response.text, file)
        # returns nothing, saves json

    response = requests.get(url, headers=headers)  # pop up for password
    raw_data = json.loads(response.text)

    print(response)
    print(type(raw_data))

    areas = raw_data["stop_areas"]  # list

    pprint(areas)

    print(type(areas))

    # area = areas[2]  # dict

    logging.info("find name and id in areas")

    list_ids = []
    list_name = []

    def fetchnameandid(self, areas, list_ids, list_name):
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

    #print(list_ids, list_name)

    # print(len(list_ids))
    # print(type(area), area)

    # print(area.keys())

    # print(area["id"])

    '''
    how to find url 
    '''
    logging.info("find url in areas json file")
    list_link = []

    def findurl(self, areas, list_link):
        for loop_link in areas:
            if type(loop_link) == dict:
                if "links" in loop_link.keys():
                    local_link = loop_link["links"]
                    list_link.append(local_link)
                else:
                    print("missing key links")
            else:
                print(f"Unexpected format {type(loop_link)}")

    # findurl()
    print(list_link)

    '''
    transform in csv file
    '''
    logging.info("transform file in csv")
    fname = "data.csv"

    def transform_in_csv(self, fname, areas):
        with open(fname, 'w') as csv_file:
            csv_file = csv.writer(csv_file)
            csv_file.writerow(["id", "name"])
            for item in areas:
                csv_file.writerow([item['id'], item['name']])

    # transform_in_csv()
    '''
    how to find name
    '''
    list_name = []

    def findname(self, areas, list_name):
        for loop_name in areas:
            if type(loop_name) == dict:
                if "name" in loop_name.keys():
                    local_name = loop_name["name"]
                    list_name.append(local_name)
                else:
                    print("missing key name")
            else:
                print(f"Unexpected format {type(loop_name)}")

    # findname()
    print(list_name)

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
    print(len(raw_data['journeys'][0]['sections'][1]['stop_date_times']))

    logging.info("fetch number of stop areas between paris and lyon")
    # for data in raw_data["journeys"]:
    # print(len(data))

    '''
    Combien de temps d'arrêts entre chacunes d'elles
    '''
    logging.info("how long does each stop have")

    stop_data = req.json()

    #list_between_eight_and_twenty = []

    logging.info("script_ended")
