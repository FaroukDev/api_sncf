import pytest

import re
import requests

from journeyInfo import JourneyInfo

STATIONS_CODES = {
    'Ermont': 'ABCD',
    'Pontoise': 'XYZ',
    'Aulnay': 'QWERTY',
    'Paris': 'TOTO'
}

STOPS = [
            {
                'stop_point': {'name': 'Ermont'},
                'base_arrival_date_time': '20210127T140900',
                'base_departure_date_time': '20210127T141000',
            },
            {
                'stop_point': {'name': 'Enghien'},
                'base_arrival_date_time': '20210127T141400',
                'base_departure_date_time': '20210127T141500',
            },
            {
                'stop_point': {'name': 'Epinay'},
                'base_arrival_date_time': '20210127T142100',
                'base_departure_date_time': '20210127T142200',
            }
        ]

def test_getURLData():
    journeyInfo = JourneyInfo()
    journeyInfo._getURLData("", auth="")

def test_updateStationsCodes():
    journey = JourneyInfo()
    regex = re.compile(r'^[\.\-() a-zA-Zéèê0-9\']{2,}$')
    assert journey._stationsCodes == {}
    areas = {'stop_areas': [
                {
                    'name': 'Ermont',
                    'id': '132456',
                },
                {
                    'name': 'Aulnay',
                    'id': '136',
                },
                {
                    'name': 'Paris',
                    'id': '132',
                }
            ]
        }
    journey._updateStationsCodes(areas, regex)
    assert journey._stationsCodes == {
                                        'Ermont': '132456',
                                        'Aulnay': '136',
                                        'Paris': '132'
                                    }
    
    journey._stationsCodes = {}
    areas = {}
    journey._updateStationsCodes(areas, regex)
    assert journey._stationsCodes == {}

    areas = {'stop_areas': [
                {
                    'name': 'Ermont',
                    'id': '132456',
                },
                {
                    'name': 'Aulnay',
                    'id': '136',
                },
                {
                    'name': 'Paris',
                    'label': '132',
                }
            ]
        }
    journey._updateStationsCodes(areas, regex)
    assert journey._stationsCodes == {
                                        'Ermont': '132456',
                                        'Aulnay': '136',
                                    }

    areas = {'stop_areas': []}
    journey._stationsCodes = {}
    journey._updateStationsCodes(areas, regex)
    assert journey._stationsCodes == {}

    areas = ['stop_areas'] # List format is unexpected, should raise TypeError
    journey._stationsCodes = {}
    journey._updateStationsCodes(areas, regex)
    assert journey._stationsCodes == {}

def test_getStationByInput(monkeypatch):
    journey = JourneyInfo()
    assert journey._departure is None
    journey._stationsCodes = STATIONS_CODES

    monkeypatch.setattr('builtins.input', lambda _: 'Ermont')
    journey._departure = journey._getStationByInput()
    assert journey._departure == ('Ermont', 'ABCD')

    monkeypatch.setattr('builtins.input', lambda _: '   Aulnay   ')
    journey._departure = journey._getStationByInput()
    assert journey._departure == ('Aulnay', 'QWERTY')

    monkeypatch.setattr('builtins.input', lambda _: 'Paris')
    journey._arrival = journey._getStationByInput()
    assert journey._arrival == ('Paris', 'TOTO')

    monkeypatch.setattr('builtins.input', lambda _: 'unknown') # Will raise KeyError
    journey._departure = None

    with pytest.raises(KeyError) as e:
        journey._getStationByInput()
    assert journey._departure == None
    assert e.type == KeyError

def test_getDepartureArrival(monkeypatch):
    journey = JourneyInfo()

    inputs = iter(['Ermont', 'Aulnay', '14:10'])
    journey._stationsCodes = STATIONS_CODES
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    journey._getDepartureArrival()
    assert journey._departure == ('Ermont', 'ABCD')
    assert journey._arrival == ('Aulnay', 'QWERTY')
    assert journey._departureTime == '14:10'

    inputs = iter(['Truc', 'Aulnay', '14:10']) # Will raise KeyError and exit with code 1
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit) as e:
        journey._getDepartureArrival()
    assert e.type == SystemExit
    assert e.value.code == 1

    inputs = iter(['Ermont', 'Aulnay', '140:10']) # Will exit with code 1 because time is badly formatted
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with pytest.raises(SystemExit) as e:
        journey._getDepartureArrival()
    assert e.type == SystemExit
    assert e.value.code == 1

def test_parseStops():
    journey = JourneyInfo()
    section = journey._parseStops(STOPS)
    assert isinstance(section, dict) is True
    assert 'section' in section
    assert len(section['section']) == len(STOPS)

    assert section['section'][0]['stop'] == 'Ermont'
    assert section['section'][0]['departure_time'] == '2021-01-27 14:10:00'

    assert section['section'][1]['stop'] == 'Enghien'
    assert section['section'][1]['departure_time'] == '2021-01-27 14:15:00'

    emptyStops = []
    stops = journey._parseStops(emptyStops)
    assert isinstance(stops, dict) is True
    assert 'section' in stops
    assert len(stops['section']) == 0

def test_parseSections():
    journey = JourneyInfo()
    sections = [{'stop_date_times': STOPS}]
    j = journey._parseSections(sections)
    assert isinstance(j, list) is True

    sections = [{'stop_date_times': []}]
    journey._parseSections(sections)
    j = journey._parseSections(sections)
    assert isinstance(j, list) is True
    assert len(j) == 0

    sections = []
    journey._parseSections(sections)
    j = journey._parseSections(sections)
    assert isinstance(j, list) is True
    assert len(j) == 0

def test_parseJourney():
    journey = JourneyInfo()
    JOURNEYS = [
        {'sections': [{'stop_date_times': STOPS}]},
        {'sections': [{'stop_date_times': STOPS}]},
        {'sections': [{'stop_date_times': STOPS}, {'stop_date_times': STOPS}]},
    ]

    journey._parseJourneys(JOURNEYS)
    assert len(journey._journeyInfo.keys()) == 3
    assert 'journey1' in journey._journeyInfo.keys()
    assert 'journey2' in journey._journeyInfo.keys()
    assert 'journey3' in journey._journeyInfo.keys()

    assert len(journey._journeyInfo['journey1']) == 1
    assert len(journey._journeyInfo['journey2']) == 1
    assert len(journey._journeyInfo['journey3']) == 2

    assert journey._journeyInfo['journey1'][0]['section'][0]['stop'] == 'Ermont'
    assert journey._journeyInfo['journey1'][0]['section'][1]['stop'] == 'Enghien'
    assert journey._journeyInfo['journey3'][1]['section'][0]['stop'] == 'Ermont'