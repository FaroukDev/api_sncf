import json
import requests
from pprint import pprint


r = requests.get('https://simplonline-v3-prod.s3.eu-west-3.amazonaws.com/media/file/txt/3fa48b7d-ce01-4268-8cbf-a3eecc8df7bb.txt')
#print(r.json())

with open('stop_areas.json',"r") as json_file:
    data = json.load(json_file)

#print(data)

#print(json.dumps(data, indent=4))

pprint(r.json())
