#!/usr/local/bin/python3

import argparse
import base64
import json
import logging
import pathlib
import os
import pprint
import re
import requests
import readline
import sys

from completer import Completer

JOURNEY_URL = "https://api.sncf.com/v1/coverage/sncf/journeys"
AREAS_URL = "https://api.sncf.com/v1/coverage/sncf/stop_areas"
LOGFILE = pathlib.Path(f'{os.getcwd()}/logs.log')

logging.basicConfig(filename=LOGFILE,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        level=logging.DEBUG,
                        datefmt='[%Y-%m-%d %H:%M:%S]')



def parseArgs():
    parser = argparse.ArgumentParser('getJourneyInfo')
    parser.add_argument('-k', '--key-file',
                        type=pathlib.Path,
                        action='store',
                        required=True,
                        help='Path of key API authentication file')
    return parser.parse_args()


def initCompletion(mapping: dict):
    readline.parse_and_bind("tab: complete")
    completer = Completer(list(mapping.keys()))
    readline.set_completer(completer.complete)

def getAPIKey(keyFile: pathlib.Path) -> str:
    with open(keyFile, 'r') as f:
        content = f.read()
    return base64.b64decode(content)

def getURLData(apiAuthKey: str, url: str) -> dict:
    res = requests.get(url, auth=(apiAuthKey, ''))
    logging.info(f"Request send to url {url}")
    if res.status_code == 200:
        data = res.json()
        logging.info(f"Request returned {res.status_code}")
    else:
        print(f'Request returned status code {res.status_code}', file=sys.stderr)
        sys.exit(1)
    return data

def getStationsMapping(apiAuthKey: str, url: str) -> tuple:
    data = getURLData(apiAuthKey, url)
    regex = re.compile(r'^[\-\.() a-zA-Zéèê]{2,}$')
    try:
        mapping = {}
        areas = data['stop_areas']
        for area in areas:
            name = area['name']
            if re.match(regex, name):
                mapping[name] = area['id']
    except KeyError as err:
        print(err)
        sys.exit(1)
    return mapping

def getDepartureArrival(mapping:  dict) -> tuple:
    departure = input("Please select departure station: ")
    arrival = input("Please select arrival station: ")
    try:
        departure = mapping[departure]
        arrival = mapping[arrival]
    except KeyError:
        logging.error("Invalid input, inexistent station")
        sys.exit(1)
    return departure, arrival


def getJourneyStats(journey: dict):
    pass

def main():
    logging.info(f"Script started")
    args = parseArgs()
    apiAuthKey = getAPIKey(args.key_file)

    mapping = getStationsMapping(apiAuthKey, AREAS_URL)
    
    initCompletion(mapping)
    departure, arrival = getDepartureArrival(mapping)
    
    journeyUrl = f'{JOURNEY_URL}?from={departure}&to={arrival}'
    journey = getURLData(apiAuthKey, journeyUrl)
    logging.info(f"Script ended")

if __name__ == '__main__':
    main()
