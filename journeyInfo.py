import datetime
import json
import logging
import os
import pathlib
import re
import readline
import requests
import sys

from completer import Completer
from logger import logger

JOURNEY_URL = "https://api.sncf.com/v1/coverage/sncf/journeys"
AREAS_URL = "https://api.sncf.com/v1/coverage/sncf/stop_areas?count=1000&start_page="

NAME = 0
CODE = 1

class JourneyInfo:
    """Class used for getting info about a journey between 2 SNCF stations"""

    def __init__(self, apiAuthKey: str = '', storage: pathlib.Path = ''):
        self._apiAuthKey = apiAuthKey
        self._stationsCodes = {} # Dict storing stations - UIC code mapping
        self._departure = None
        self._arrival = None
        self._departureTime = None
        self._journeyInfo = {} # List of possible journeys
        self._storage = storage

    @logger
    def _initCompletion(self):
        readline.parse_and_bind("tab: complete")
        completer = Completer(list(self._stationsCodes.keys()))
        readline.set_completer_delims('')
        readline.set_completer(completer.complete)

    @logger
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

    @logger
    def _getStationsCodes(self, url: str = ""):
        """Two scenarios: If script is run for the first time then it send requests API to get stations UIC Codes
            Then those codes are saved as a json in data/ directory: ./data/stations_code.json
            So, if data/stations_code.json exists, then no need to requests API but just load the json instead in stationsCodes attribute
        """
        regex = re.compile(r'^[\.\-() a-zA-Zéèê0-9\']{2,}$')
        try:
            with open(self._storage, 'r') as codes:
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

    @logger
    def _saveStationsCodes(self):
        try:
            os.mkdir("data", 0o744)
        except FileExistsError:
            pass
        finally:
            with open(self._storage, "w") as codes:
                json.dump(self._stationsCodes, codes, indent=4)

    @logger
    def _updateStationsCodes(self, data: dict, regex):
        try:
            if 'stop_areas' in data:
                areas = data['stop_areas']
                for area in areas:
                    if 'name' in area:
                        name = area['name']
                        if re.match(regex, name) and 'id' in area:
                            self._stationsCodes[name] = area['id']
        except TypeError as err:
            logging.info(f"Unable to retrieve station/code mapping. Unexpected format {err}")

    def _getStationByInput(self, doa=''):
        station = input(f"Please type {doa} station: ").strip()
        return (station, self._stationsCodes[station])

    def _getDepartureTime(self):
        timeRegex = re.compile(r'^((2[0-3]|[0-1][0-9]):[0-5][0-9])|$')
        departureTime = input("Please type time of departure (hh:mm):").strip()
        if not re.match(timeRegex, departureTime):
            logging.error("Incorrect date format")
            sys.exit(1)
        return departureTime

    @logger
    def _getDepartureArrival(self):
        try:
            self._departure = self._getStationByInput("departure")
            self._arrival = self._getStationByInput("arrival")
            self._departureTime = self._getDepartureTime()
        except KeyError as err:
            logging.error(f'Missing key {err}')
            sys.exit(1)
        except EOFError:
            logging.error("Ctrl + D pressed ")
            sys.exit(2)

    @logger
    def _parseJourneys(self, journeys: list):
        for n, journey in enumerate(journeys, 1):
            if isinstance(journey, dict) and 'sections' in journey:
                sections = journey['sections']
                self._journeyInfo['journey' + str(n)] = self._parseSections(sections)

    def _parseSections(self, sections: list) -> list:
        newJourney = []
        for section in sections:
            if 'stop_date_times' in section:
                stops = section['stop_date_times']
                newSection = self._parseStops(stops)
                if newSection['section']:
                    newJourney.append(newSection)
        return newJourney

    def _parseStops(self, stops: list) -> dict:
        newSection = {'section': []}
        for stop in stops:
            newStop = {}
            newStop['stop'] = stop['stop_point']['name']
            dateDeparture = datetime.datetime.strptime(stop['base_arrival_date_time'], "%Y%m%dT%H%M%S")
            dateArrival = datetime.datetime.strptime(stop['base_departure_date_time'], "%Y%m%dT%H%M%S")
            newStop['arrival_time'] = dateDeparture.strftime("%Y-%m-%d %H:%M:%S")
            newStop['departure_time'] = dateArrival.strftime("%Y-%m-%d %H:%M:%S")
            newStop['time_delta'] = str(dateArrival - dateDeparture)
            newSection['section'].append(newStop)
        return newSection

    @logger
    def _getJourneyInfo(self):
        ''' Functions fill dict with main informations concerning selected journey, formatted as:
            Departure time
            Duration
            Arrival Time
            Array of stops : Station name
                             Time of arrival at stop
        '''
        journey = self._getURLData(f'{JOURNEY_URL}?from={self._departure[CODE]}&to={self._arrival[CODE]}')
        if 'error' in journey:
            print(journey['error']['message'])
            sys.exit(1)
        try:
            journeys = journey['journeys']
            self._parseJourneys(journeys)
            with open(self._storage, "w", encoding='utf8') as f:
                json.dump(self._journeyInfo, f, indent=4)
            logging.info(f"Journey info stored in {self._storage}")
        except KeyError as err:
            logging.error(f'Missing key {err}')
        except TypeError as err:
            logging.error(f"{err}: Unexpected format")
            sys.exit(1)

    @logger
    def run(self):
        self._getStationsCodes(AREAS_URL)
        self._initCompletion()
        self._getDepartureArrival()
        self._getJourneyInfo()