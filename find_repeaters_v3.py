import os
import time
from obspy.core import read
from datetime import date
from obspy.geodetics.base import gps2dist_azimuth
import json
import utils
import argparse

config = utils.load_configuration()

today         = date.today()
start_time    = time.time()

root = config['root']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--station', type=str, help = 'Station id.') 
    args = parser.parse_args()
    station = args.station

    print("Loading data in memory for station:  " + station)
    master = read(os.path.join(root, station.upper(), 'sac', '*HZ*.sac'))
    print("Number of waveforms = "+ str(len(master)))
