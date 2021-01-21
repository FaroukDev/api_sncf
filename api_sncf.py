#!/usr/local/bin/python3

import argparse
import csv
import json
import requests
import sys

URL = "https://api.sncf.com/v1/coverage/sncf/stop_areas"

def parseArgs():
    parser = argparse.ArgumentParser('api-sncf')
    parser.add_argument('-k', '--key', type=str, action='store', required=True, help='Key for API authentication')
    return parser.parse_args()

def getDataFromApi(url: str, key: str):
    res = requests.get(URL, auth=(key, ''))
    if res.status_code == 200:
        data = res.json()
    else:
        print(f'Request status code returned {res.status_code}', file=sys.stderr)
        sys.exit(1)
    return data

def saveDataToCsv(data):
    """ Create a CSV file based on data : Columns are : Code_gare, nom, latitude, longitude, info_admin"""

    header = ['Code', 'Name', 'Latitude', 'Longitude', 'Info']
    with open("stations.csv", 'w', newline='') as csvStations:
        writer = csv.DictWriter(csvStations, fieldnames=header)
        writer.writeheader()
        stop_areas = data['stop_areas']
        for stop in stop_areas:
            if 'codes' in stop:
                code = stop['codes'][0]['value']
            else:
                code = ''
            name = stop['name']
            lat = stop['coord']['lat']
            lon = stop['coord']['lon']
            writer.writerow({'Code': code, 'Name': name, 'Latitude': lat, 'Longitude': lon})

def main():
    args = parseArgs()
    data = getDataFromApi(URL, args.key)
    saveDataToCsv(data)

main()

