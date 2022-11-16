import os
import time
from obspy.core import read
from datetime import date
from obspy.geodetics.base import gps2dist_azimuth
import json
import utils
import time
import argparse
from tqdm import tqdm

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
    start = time.time()
    master = read(os.path.join(root, station.upper(), 'sac', '*HZ*.sac'))
    N = len(master)
    end = time.time()
    print("Number of waveforms = "+ str(N), ' time elapsed: ', end-start, 's.')
    master.filter('bandpass', 
            freqmin=config['low_f'] , 
            freqmax=config['high_f'], 
            corners=config['n_poles'], 
            zerophase=True )

    for k, tr in enumerate(tqdm(master)):
        kevnm_master = tr.stats.sac.kevnm.rstrip()
        for n in range(k+1,N):
                pass


