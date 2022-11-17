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
import numpy as np
from matplotlib import pyplot as plt

config = utils.load_configuration()
today         = date.today()
start_time    = time.time()

root = config['root']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--station', type=str, help = 'Station id.') 
    parser.add_argument('-t', '--test',action='store_true', help='-t unit test.') 
    args = parser.parse_args()
    station = args.station
    unit_test = args.test

    if unit_test:
        print('UNIT TEST: ')
        waveforms = read(os.path.join(os.getcwd(),'test_data','*sac'))
        print(waveforms)
    else:
        print("Loading data in memory for station:  " + station)
        start = time.time()
        waveforms = read(os.path.join(root, station.upper(), 'sac', '*HZ*.sac'))
        end = time.time()
        print("Number of waveforms = "+ str(N), ' time elapsed: ', end-start, 's.')

    N = len(waveforms)
    waveforms.filter('bandpass', 
            freqmin=config['low_f'] , 
            freqmax=config['high_f'], 
            corners=config['n_poles'], 
            zerophase=True )

    for k in tqdm(range(0,N)):
        kevnm_master = waveforms[k].stats.sac.kevnm.rstrip()
        ds_master = waveforms[k].stats.sampling_rate
        t5_master = waveforms[k].stats.sac.t5 - 1.5
        id_master = np.searchsorted(waveforms[k].times(
                reftime=waveforms[k].stats.starttime - waveforms[k].stats.sac.b), 
                t5_master, side="left")
        master = waveforms[k].data[id_master:id_master+config['Win']]
        print('t5: ', t5_master)
        print('id: ', id_master)
        print('N: ', len(master))
        for n in range(k+1,N):
            t5_test = waveforms[n].stats.sac.t5 - 1.5
            dt_test = waveforms[k].stats.sampling_rate
            id_test = np.searchsorted(waveforms[n].times(
                                      reftime=waveforms[n].stats.starttime - waveforms[n].stats.sac.b), 
                                      t5_test, side="left")
            test = waveforms[n].data[id_test:id_test+config['Win']]

            fig, ax = plt.subplots(2,1)
            t = np.linspace(0, (config['Win']-1)/ds_master, config['Win'])
            ax[0].plot(t,master)
            ax[1].plot(t,test)
            fig.savefig('plot_' + str(k) + '_' + str(n) + '.png')
            plt.close()






        
            


