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
import numba as nb

config = utils.load_configuration()
today         = date.today()
start_time    = time.time()
before_p_wave = 1.5

root = config['root']

plotting = False

#@nb.jit
def get_correlation_coefficient(S1, S2, dt):
    ''' signal mut be centered at p-wave arrival minus two seconds'''
    N = len(S1)
    Power_S1 = max(np.correlate(S1,S1))/N
    Power_S2 = max(np.correlate(S2,S2))/N

    if (Power_S1 == 0) or (Power_S2 == 0):
        CorrelationCoefficient = 0
        tshift                 = 0
    else:
        A = np.correlate(S1,S2,'full')/(N*np.sqrt(Power_S1*Power_S2))
        time2 = np.arange(-(N-1)*dt, N*dt, dt)
        CorrelationCoefficient = A.max()
        index = np.argmax(A)
        tshift = time2[index]

    return CorrelationCoefficient, tshift


#@nb.jit(nopython=True)
def processing(waveforms_numpy, N, kevnm, dsampling_rate, datetimes, Threshold, 
               low_f, high_f, Win,plotting = False):
    output_list = []
    print('N: ', N)

    #N = 5
    for k in tqdm(range(0,N)):
        Power_S1 = max(np.correlate(waveforms_numpy[k,:],waveforms_numpy[k,:]))/Win
        dt = 1/dsampling_rate[k]
        if Power_S1 != 0:
            for n in range(k+1,N):
                Power_S2 = max(np.correlate(waveforms_numpy[n,:],waveforms_numpy[n,:]))/Win
                if Power_S2 == 0:
                    CorrelationCoefficient = 0
                    tshift                 = 0
                else:    
                    A = np.correlate(waveforms_numpy[k,:],waveforms_numpy[n,:],'full')/(Win*np.sqrt(Power_S1*Power_S2))
                    time2 = np.arange(-(Win-1)*dt, Win*dt, dt)
                    CorrelationCoefficient = A.max()
                    index = np.argmax(A)
                    tshift = time2[index]
                
                #CorrelationCoefficient, tshift = get_correlation_coefficient(waveforms_numpy[k,:], waveforms_numpy[n,:], 1/dsampling_rate[k])
                #print(CorrelationCoefficient, ' - ', CorrelationCoefficient2)
                if CorrelationCoefficient >= Threshold:
                    coherence = crs.coherency(waveforms_numpy[k,:], waveforms_numpy[n,:], low_f, high_f, dsampling_rate[k])
                    #coherence = 0.97
                    outline = (datetimes[k], datetimes[n], CorrelationCoefficient, 
                               coherence, kevnm[k], kevnm[n])
                    #print(outline)
                    #int(round(coherence*1e4)), '%08d' % (int(kevnm[k])), '%08d' % (int(kevnm[n])))
                    output_list.append(outline)
            
            #print('cc: ', round(CorrelationCoefficient*1e4), ' coh: ', round(coherence*1e4))
            
                #if plotting:
                #    fig, ax = plt.subplots(3,1, figsize=(22, 12))
                #    t = np.linspace(0, (Win-1)/dsampling_rate[k], Win)
                #    ax[0].plot(t,waveforms_numpy[k,:], color='black', linewidth=0.5)
                #    ax[1].plot(t,waveforms_numpy[n,:], color='black', linewidth=0.5)
                #    ax[2].plot(t,waveforms_numpy[k,:]/np.max(np.abs(waveforms_numpy[k,:])), linewidth = 0.4)
                #    ax[2].plot(t, crs.FFTshift(waveforms_numpy[n,:]/np.max(np.abs(waveforms_numpy[n,:])),float(tshift*dsampling_rate[n])), linewidth = 0.4)
                #    fig.savefig('plot_' + str(kevnm[k]) + '_' + str(kevnm[n]) + '.png')
                #    plt.close()
    return output_list

def convert_obspy_numpy(waveforms, N):
    kevnm = np.zeros(N)
    dsampling_rate = np.zeros(N)
    datetimes = nb.typed.List()

    waveforms_numpy = np.zeros((N, config['Win']))
    for k, tr in enumerate(waveforms):
        datetimes.append(datetime.datetime.strftime(waveforms[k].stats.starttime.datetime,'%Y.%j.%H%M%S'))
        kevnm[k] = tr.stats.sac.kevnm.rstrip()
        dsampling_rate[k] = tr.stats.sampling_rate
        if hasattr(tr.stats.sac,'t5'):
            t5 = tr.stats.sac.t5 - before_p_wave
        else:
            t5 = tr.stats.sac.a - before_p_wave

        id_master = np.searchsorted(tr.times(
                reftime=tr.stats.starttime - tr.stats.sac.b), 
                t5, side="left")
        master = tr.data[id_master:id_master+config['Win']]
        if len(master) != config['Win']:
            continue # The record is incomplete, this will make CC=0
        waveforms_numpy[k,:] = master

        
    return waveforms_numpy, kevnm, dsampling_rate, datetimes
    



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

    waveforms_numpy, kevnm, dsampling_rate, datetimes = convert_obspy_numpy(waveforms, N)


    start = time.time()
    output_list =  processing(waveforms_numpy, N, kevnm, dsampling_rate, datetimes, 
                              config['Threshold'], config['low_f'], config['high_f'],
                              config['Win'], True)
    end = time.time() 
    print('Time elapsed: ', end - start, 's.')

    #print(output_list)
    df_final = pd.DataFrame.from_dict(output_list)
    df_final[2] = df_final[2].apply(lambda x: x*1e4).astype('int')
    df_final[3] = df_final[3].apply(lambda x: x*1e4).astype('int')
    df_final[4] = df_final[4].astype('int').apply(lambda x: f"{x:08d}")
    df_final[5] = df_final[5].astype('int').apply(lambda x: f"{x:08d}")
    print(df_final.head())
    df_final.to_csv(r'pandas.txt', header=None, index=None, sep=' ')




        
            


