from scipy import fftpack, signal
import numpy as np
import math
import cmath

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

def FFTshift(signal, delay):
    x = signal
    N = len(x)
    R = range(1,N+1)

    X = fftpack.fft(x)
    k = np.concatenate((range(0,int(math.floor(N/2))),range(int(math.floor(-N/2)),0)))
    W = np.exp(-cmath.sqrt(-1) * 2 * np.pi * delay * k / N)
    if N%2 == 0:
        W[int(N/2)] = W[int(N/2)].real

    Y = X*W
    y = fftpack.ifft(Y)
    y = y.real
    return y

def coherency(*args):
# Input arguments:
#  S1 - Signal 1 numpy array
#  S2 - Signal 2 numpy array
#  f1 - Minimum frquency
#  f2 - Maximum frequency
#  fs - Sampling frequency
    nargin = len(args)

    if nargin == 0:
        sac1 = read('./test_data/20080925043418.IG.PLIG.BHZ.sac')
        sac2 = read('./test_data/20011105104504.IG.PLIG.BHZ.sac')
        S1   = sac1[0].data
        S2   = sac2[0].data
        fs   = sac2[0].stats.sampling_rate
        fmin = 1.0
        fmax = 8.0
        filename = 'test.dat'
    elif nargin == 5:
        S1       = args[0]
        S2       = args[1]
        fmin     = args[2]
        fmax     = args[3]
        fs       = args[4]
    else:
        sys.exit('Invalid number of input arguments - crsmex.coherency')

    N1  = len(S1)
    N2  = len(S2)
    #Cxy, f = matplotlib.mlab.cohere(S1,S2,Fs=fs,NFFT=128)
    f, Cxy = signal.coherence(S1, S2, fs=fs)
    f_ind  = np.where((f >= fmin) & (f <= fmax))
    Cxy_mean = np.mean(np.sqrt(Cxy[f_ind]))
    out = np.array([f, Cxy])

    #if Cxy_mean >= 0.8:
    #     print 'Writting coherency ', filename
    #     np.savetxt(filename,np.transpose(out),fmt='%-8.3f %7.5f')
    return Cxy_mean
