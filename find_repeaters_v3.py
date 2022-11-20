import os
import time
from obspy.core import read
from datetime import date
from obspy.geodetics.base import gps2dist_azimuth
import json
import utils
import time
import datetime
import argparse
from tqdm import tqdm
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import crsmex as crs
from numba import jit

config = utils.load_configuration()
today         = date.today()
start_time    = time.time()

root = config['root']

plotting = False

#@jit(nopython=True)
def processing(waveforms, N, plotting = False):
    output_list = []

    for k in tqdm(range(0,N)):
        kevnm_master = waveforms[k].stats.sac.kevnm.rstrip()
        ds_master = waveforms[k].stats.sampling_rate
        t5_master = waveforms[k].stats.sac.t5 - 1.5
        id_master = np.searchsorted(waveforms[k].times(
                reftime=waveforms[k].stats.starttime - waveforms[k].stats.sac.b), 
                t5_master, side="left")
        master = waveforms[k].data[id_master:id_master+config['Win']]
        datetime_master = datetime.datetime.strftime(waveforms[k].stats.starttime.datetime,'%Y.%j.%H%M%S')
        for n in range(k+1,N):
            t5_test = waveforms[n].stats.sac.t5 - 1.5
            ds_test = waveforms[k].stats.sampling_rate
            id_test = np.searchsorted(waveforms[n].times(
                                      reftime=waveforms[n].stats.starttime - waveforms[n].stats.sac.b), 
                                      t5_test, side="left")
            test = waveforms[n].data[id_test:id_test+config['Win']] 
            try:
                CorrelationCoefficient, tshift = crs.get_correlation_coefficient(master, test, 1/ds_master)
            except:
                print('k: ', k, ' n: ', n)
                exit()
            
            if CorrelationCoefficient >= config['Threshold']:
                kevnm_test = waveforms[n].stats.sac.kevnm.rstrip()
                coherence = crs.coherency(master, test, config['low_f'], config['high_f'], ds_master)
                datetime_test = datetime.datetime.strftime(waveforms[n].stats.starttime.datetime,'%Y.%j.%H%M%S')
                outline = {1 : datetime_master, 2 : datetime_test, 3 :
                        int(round(CorrelationCoefficient*1e4)), 4 : int(round(coherence*1e4)), 
                        5 : '%08d' % (int(kevnm_master)), 6: '%08d' % (int(kevnm_test))}
                output_list.append(outline)
            
            #print('cc: ', round(CorrelationCoefficient*1e4), ' coh: ', round(coherence*1e4))
            
            if plotting:
                fig, ax = plt.subplots(3,1, figsize=(22, 12))
                t = np.linspace(0, (config['Win']-1)/ds_master, config['Win'])
                ax[0].plot(t,master, color='black', linewidth=0.5)
                ax[1].plot(t,test, color='black', linewidth=0.5)
                ax[2].plot(t, crs.FFTshift(master/np.max(np.abs(master)),float(tshift*ds_master)), linewidth = 0.4)
                ax[2].plot(t, crs.FFTshift(master/np.max(np.abs(master)),float(tshift*ds_master)), linewidth = 0.4)
                fig.savefig('plot_' + str(k) + '_' + str(n) + '.png')
                plt.close()
    return output_list

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

    N = len(waveforms)
    print("Number of waveforms = "+ str(N), ' time elapsed: ', end-start, 's.')
    waveforms.filter('bandpass', 
            freqmin=config['low_f'] , 
            freqmax=config['high_f'], 
            corners=config['n_poles'], 
            zerophase=True )


    start = time.time()
    output_list =  processing(waveforms, N)
    end = time.time(    
    print('Time elapsed: ', end - start, 's.')

    df_final = pd.DataFrame.from_dict(output_list)
    print(df_final.head())
    df_final.to_csv(r'pandas.txt', header=None, index=None, sep=' ')




        
            


