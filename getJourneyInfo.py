#!/usr/local/bin/python3
import argparse
import datetime
import json
import logging
import pathlib
import os
import re
import requests
import readline
import sys

from completer import Completer

JOURNEY_URL = "https://api.sncf.com/v1/coverage/sncf/journeys"
AREAS_URL = "https://api.sncf.com/v1/coverage/sncf/stop_areas?count=1000&start_page="
LOGFILE = pathlib.Path(f'{os.getcwd()}/logs.log')

logging.basicConfig(filename=LOGFILE,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        level=logging.DEBUG,
                        datefmt='[%Y-%m-%d %H:%M:%S]')


def getAPIKey(keyFile: pathlib.Path) -> str:
    with open(keyFile, 'r') as f:
        content = f.read()
    return content

class JourneyInfo:
    """Class used for getting info about a journey between 2 SNCF stations"""

    def __init__(self, apiAuthKey: str):
        self._apiAuthKey = apiAuthKey
        self._stationsCodes = {} # Dict storing stations - UIC code mapping
        self._departure = None
        self._arrival = None
        self._journeyInfo = {} # List of possible journeys

    def _initCompletion(self):
        readline.parse_and_bind("tab: complete")
        completer = Completer(list(self._stationsCodes.keys()))
        readline.set_completer_delims('')
        readline.set_completer(completer.complete)

    def _getURLData(self, url: str) -> dict:
        res = requests.get(url, auth=(self._apiAuthKey, ''))
        logging.info(f"Request send to url {url}")
        if res.status_code == 200:
            data = res.json()
            logging.info(f"Request returned {res.status_code}")
        else:
            logging.error(f"Request returned {res.status_code}")
            sys.exit(1)
        return data

    def _updateStationsCodes(self, data: dict, regex):
        try:
            areas = data['stop_areas']
            for area in areas:
                name = area['name']
                if re.match(regex, name) and area.get('id'):
                    self._stationsCodes[name] = area['id']
        except KeyError as err:
            logging.error(f'Missing key {err}')

    def _saveStationsCodes(self):
        os.mkdir("data", 0o744)
        with open("data/stations_codes.json", "w") as codes:
            json.dump(self._stationsCodes, codes, indent=4)

    def _getStationsCodes(self, url: str) -> tuple:
        """Two scenarios: If script is run for the first time then it send requests API to get stations UIC Codes
            Then those codes are saved as a json in data/ directory : ./data/stations_code.json
            So, if data/stations_code.json exists, then no need to requests API but just load the json instead in stationsCodes attribute
        """
        regex = re.compile(r'^[\.\-() a-zA-Zéèê]{2,}$')
        try:
            with open("data/stations_codes.json", 'r') as codes:
                self._stationsCodes = json.load(codes)
        except (FileNotFoundError, PermissionError) as err:
            logging.info(f'{err}: Unable to retrieve stations codes locally. Sending requests to API')
            start_page = 0
            while True:
                data = self._getURLData(f'{url}{start_page}')
                if data['pagination']['items_on_page'] == 0:
                    break
                self._updateStationsCodes(data, regex)
                start_page += 1
            self._saveStationsCodes()

    def _getDepartureArrival(self):
        departure = input("Please select departure station: ").strip()
        arrival = input("Please select arrival station: ").strip()
        try:
            self._departure = self._stationsCodes[departure]
            self._arrival = self._stationsCodes[arrival]
        except KeyError as err:
            logging.error(f'Missing key {err}')
            sys.exit(1)
        except (EOFError, KeyboardInterrupt):
            pass

    def _getJourneyInfo(self):
        ''' Functions fill dict with main informations concerning selected journey, formatted as:
            Departure time
            Duration
            Arrival Time
            Array of stops : Station name
                             Time of arrival at stop
        '''

        journey = self._getURLData(f'{JOURNEY_URL}?from={self._departure}&to={self._arrival}')
        if 'error' in journey:
            print(journey['error']['message'])
            sys.exit(1)
        try:
            journeys = journey['journeys']
            journeyNumber = 1
            for journey in journeys:
                print("="*25,f"\nJourney N.{journeyNumber}\n","="*25)
                if type(journey) == dict and 'sections' in journey:
                    sections = journey['sections']
                    for section in sections:
                        if 'stop_date_times' in section:
                            stops = section['stop_date_times']
                            for stop in stops:
                                stop_name = stop['stop_point']['name']
                                arrivalTime = stop.get('base_arrival_date_time')
                                date = datetime.datetime.strptime(arrivalTime, "%Y%m%dT%H%M%S")
                                print(f'{stop_name:25} {date}')
                            print("-------CORRESPONDANCE------")
                    journeyNumber += 1
        except KeyError as err:
            logging.error(f'Missing key {err}')

    def _displayJourneys(self):
        pass

    def run(self):
        self._getStationsCodes(AREAS_URL)
        self._initCompletion()
        self._getDepartureArrival()
        self._getJourneyInfo()

def parseArgs():
    parser = argparse.ArgumentParser('getJourneyInfo')
    parser.add_argument('-k', '--key-file',
                        type=pathlib.Path,
                        action='store',
                        required=True,
                        help='Path of key API authentication file')
    return parser.parse_args()


def main():
    logging.info(f"Script started")
    args = parseArgs()
    apiAuthKey = getAPIKey(args.key_file)
    journey = JourneyInfo(apiAuthKey)
    journey.run()
    logging.info(f"Script ended")

if __name__ == '__main__':
    main()
