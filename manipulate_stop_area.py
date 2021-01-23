import pprint
import json
import requests
import csv
import logging

logging.basicConfig(filename='data.log', level=logging.DEBUG)
logging.info("Script started")

url = "https://api.sncf.com/v1/coverage/sncf/stop_areas"
headers = {"Authorization": "6df7dc97-1bdc-4539-af03-9d854dd236fe"}
response = requests.get(url, headers=headers) #pop up for password
raw_data = json.loads(response.text)

print(response)
print(type(raw_data))

areas = raw_data["stop_areas"] #list

print(type(areas))

area = areas[2] #dict

list_ids = []
list_name = []


logging.info("find name and id in areas")
for loop_area, loop_name in zip(areas, areas):
    if type(loop_area) == dict and type(loop_name) ==  dict:
        if "id" in loop_area.keys() and "name" in loop_name.keys(): #!!!!!!
            local_id = loop_area["id"]
            local_name = loop_name["name"]
            list_ids.append(local_id)
            list_name.append(local_name)
        else:
            print("Missing key id")
    else:
        print(f"Unexpected format {type(loop_area)}")

print(list_ids, list_name)


# print(type(area), area)

#print(area.keys())

# print(area["id"])


'''
how to find url 
'''
logging.info("find url in areas json file")
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
    
#print(list_link)

#print(area)

'''
transform in csv file
'''
logging.info("transform file in csv")
fname = "data.csv"

with open(fname, 'w') as csv_file:
    csv_file = csv.writer(csv_file)
    csv_file.writerow(["id","name"])
    for item in areas:
        csv_file.writerow([item['id'], item['name']])
        
        





'''
how to find name
'''
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
#print(list_name)

logging.info("script_ended")