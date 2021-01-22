import pprint
import json
import requests
import csv

url = "https://api.sncf.com/v1/coverage/sncf/stop_areas"
headers = {"Authorization": "e3f2b3a6-caa9-47d7-98ee-1f67379e654b"}
response = requests.get(url, headers=headers) #pop up for password
raw_data = json.loads(response.text)

print(response)
print(type(raw_data))

areas = raw_data["stop_areas"] #list

print(type(areas))

area = areas[2] #dict

list_ids = []

for loop_area in areas:
    if type(loop_area) == dict:
        if "id" in loop_area.keys(): #!!!!!!
            local_id = loop_area["id"]
            list_ids.append(local_id)
        else:
            print("Missing key id")
    else:
        print(f"Unexpected format {type(loop_area)}")

print(len(list_ids))


# print(type(area), area)

# print(area.keys())

# print(area["id"])


'''
how to find url 
'''

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
    
print(len(list_link))