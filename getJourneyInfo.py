#!/usr/local/bin/python3
import argparse
import logging
import pathlib
import os
import signal
import sys

from journeyInfo import JourneyInfo
from logger import logger

LOGFILE = pathlib.Path(f'{os.getcwd()}/logs.log')

logging.basicConfig(filename=LOGFILE,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        level=logging.DEBUG,
                        datefmt='[%Y-%m-%d %H:%M:%S]')

@logger
def getAPIKey(keyFile: pathlib.Path) -> str:
    with open(keyFile, 'r') as f:
        content = f.read()
    return content

@logger
def handleSigInt(sigNum, stackFrame=None):
    logging.info("Ctrl-C pressed. Exiting script")
    sys.exit(130)

@logger
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
    signal.signal(signal.SIGINT, handleSigInt)
    args = parseArgs()
    try:
        apiAuthKey = getAPIKey(args.key_file)
    except (FileNotFoundError, PermissionError) as err:
        logging.error(err)
        sys.exit(1)
    journey = JourneyInfo(apiAuthKey, "data/stations_codes.json")
    journey.run()
    logging.info(f"Script ended")

if __name__ == '__main__':
    main()
