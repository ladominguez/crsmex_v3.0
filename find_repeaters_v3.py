import os
from obspy.core import read
from datetime import date
from obspy.geodetics.base import gps2dist_azimuth
import json
import utils

config = utils.load_configuration()

today         = date.today()
start_time    = time.time()

path_data = os.path.join(config['root'],'sac')

if __name__ == '__main__':
    print("Loading data in memory from " + path_data)
    master    = read(os.path.join(path_data,'sac','*HZ*.sac'))
    print("Number of waveforms = "+ str(len(master)))