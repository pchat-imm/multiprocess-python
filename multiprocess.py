from multiprocessing import Process, Queue
import numpy as np
import scipy
import csv
from py3gpp import *

############################################################
# FUNCTION DEFINITIONS
############################################################
def load_rx_srsRAN(input_file):
  #'''load a file of receive signal from base station (SDR) using srsRAN'''
  waveform = []
  with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
      IQComplex = row[0].strip()
      IQComplex = IQComplex.replace('i','j')
      IQComplex = complex(IQComplex)
      waveform.append(IQComplex)
  return waveform

def waveform_fshift(fshift, sampleRate, waveform):
  # '''frequency shift waveform'''
  t = np.arange(len(waveform))/sampleRate
  rxWaveformFreqCorrected = waveform * np.exp(-1j*2*np.pi*fshift*t)
  return rxWaveformFreqCorrected

def waveformDS(sampleRate, waveform):
  # '''downsampling waveform'''
  mu = 1
  scs = 15 * 2**mu
  syncNfft = 256                  # minimum FFT Size to cover SS burst
  syncSR = syncNfft * scs * 1e3
  rxWaveformDS = scipy.signal.resample_poly(waveform, syncSR, sampleRate)
  return rxWaveformDS

def load_PSS_seq(base_path_PSS):
  #'''load all PSS_seq to use as refWaveform'''
  NID2_val = [0,1,2]

  # Dictionary to store file path and refWaveform
  PSS_files = {}
  refWaveforms = {}

  # Generate file path and initialize refWaveform arrays - add lists in the dictionary
  for NID2 in NID2_val:
      PSS_files[f'NID2_{NID2}'] = f'{base_path_PSS}/NID2_{NID2}.csv'
      refWaveforms[f'NID2_{NID2}'] = []

  for NID2 in NID2_val:
      with open(PSS_files[f'NID2_{NID2}'], 'r') as f:
          reader = csv.reader(f)
          for row in reader:
              IQ_PSS = row[0].strip()     # get string
              IQ_PSS = complex(IQ_PSS)    # turn to complex
              refWaveforms[f'NID2_{NID2}'].append(IQ_PSS)
  print("complete load_PSS_seq!")
  return refWaveforms

def correlate(carrier, fshifts, sampleRate, rxWaveformDS, refWaveforms):
   # '''correlate 1 rxWaveformDS of a fshift with 3 refWaveforms''' 
  kPSS = np.arange((119-63), (119+64))    # np.arange(56, 183) # check on 3GPP standard 
  corr_ind = np.zeros(3, 'int')    # array
  corr_val = np.zeros(3)
  t = np.arange(len(rxWaveformDS))/sampleRate

  for NID2 in np.arange(3, dtype='int'):
    temp = scipy.signal.correlate(rxWaveformDS, refWaveforms[f'NID2_{NID2}'],'valid')
    corr_ind[NID2] = np.argmax(np.abs(temp))
    corr_val[NID2] = np.abs(temp[corr_ind[NID2]])
  # print("corr_ind ", corr_ind)
  # print("corr_val ", corr_val)  
  return corr_ind, corr_val

def peak_one_fshift(fshift_val, corr_ind, corr_val):
  # '''get peak corr_val of the fshift (rxWaveformDS with 3 refWaveforms)'''
  # input is 3 NID2 with 3 corr_ind and 3 corr_val 
  fshift_NID2 = np.argmax(corr_val)
  fshift_corr_val = corr_val[fshift_NID2]
  fshift_corr_ind = corr_ind[fshift_NID2]
  print("fshift_corr: ", {fshift_val}, {fshift_NID2}, {fshift_corr_ind}, {fshift_corr_val})    
  return fshift_NID2, fshift_corr_ind, fshift_corr_val

############################################################
# ADDED DEFINITIONS
############################################################
def processing_fshift(fshift, sampleRate, carrier, waveform, refWaveforms, Queue):
    # print("input fshift: ", fshift)
    rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
    rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)
    temp_corr_ind, temp_corr_val = correlate(carrier, fshift, sampleRate, rxWaveformDS, refWaveforms)
    fshift_NID2, fshift_corr_ind, fshift_corr_val = peak_one_fshift(fshift, temp_corr_ind, temp_corr_val)

    Queue.put((fshift, fshift_NID2, fshift_corr_ind, fshift_corr_val))

    # print(Queue.qsize())

    return fshift_NID2, fshift_corr_ind, fshift_corr_val

# def get_queue(Queue):
#     fshift_corr = []
#     while not Queue.empty():
#         fshift_corr.append(Queue.get())

#     print("fshift_corr: ", fshift_corr)

def get_all_fshift_corr(Queue):
    # '''currently get user_input through terminal, will need to change to subscribe mqtt topic and get message'''
    fshift_corr = {}
    while not Queue.empty():
        payload = Queue.get()  # Retrieve data from the Queue
        
        fshift_val = int(payload[0])      # 45000 
        fshift_NID2 = int(payload[1])     # 1 
        fshift_corr_ind = int(payload[2]) # 212347 
        fshift_corr_val = float(payload[3])  # 2.345 

        # Store correlated values in dictionary
        fshift_corr[f'fshift_{fshift_val}'] = {
            "fshift_data": fshift_val,
            "fshift_NID2": fshift_NID2,
            "fshift_corr_ind": fshift_corr_ind,
            "fshift_corr_val": fshift_corr_val
        }

    # Print all the correlated values
    for key, value in fshift_corr.items():
        print(f"{key}: {value}")
        
    return fshift_corr

def max_fshift_corr(fshift_corr):
  # ''' select fshift that provide the highest corr_val '''
  # use list comprehension to get list of corr_val
  list_corrVal = [x['fshift_corr_val'] for x in fshift_corr.values()]
  max_ind = np.argmax(list_corrVal)  # find index of list_corrVal with max corr\
  # return fshift of fshift_corr.keys at the max_ind
  sel_fshift = list(fshift_corr.keys())[max_ind]    # fshift_corr.keys() = ['fshift_30000', 'fshift_45000'], sel_fshift = 'fshift_45000'
  # return NID2, corr_ind, corr_val at that fshift
  sel_NID2     = fshift_corr[sel_fshift]['fshift_NID2']
  sel_corr_ind = fshift_corr[sel_fshift]['fshift_corr_ind']
  sel_corr_val = fshift_corr[sel_fshift]['fshift_corr_val']
  print(f"---max_fshift_corr---sel_fshift {sel_fshift}, sel_NID2 {sel_NID2}, sel_corr_ind {sel_corr_ind}, sel_corr_val {sel_corr_val}")
  return sel_fshift, sel_NID2, sel_corr_ind, sel_corr_val

def process_max_corr(Queue):
   fshift_corr = get_all_fshift_corr(Queue)
   sel_fshift, sel_NID2, sel_corr_ind, sel_corr_val = max_fshift_corr(fshift_corr)

   return sel_fshift, sel_NID2, sel_corr_ind, sel_corr_val


if __name__ == "__main__":
    # init parameter
    sampleRate = 15.36e6
    nrbSSB = 20
    mu = 1
    scs = 15 * 2**mu
    syncNfft = 256                  # minimum FFT Size to cover SS burst
    syncSR = syncNfft * scs * 1e3
    carrier = nrCarrierConfig(NSizeGrid = nrbSSB, SubcarrierSpacing = scs)

    print("load files")
    base_path_PSS = "./PSS_Seq"
    input_file = "./waveform_IQComplex_fllay.csv"
    waveform = load_rx_srsRAN(input_file)
    refWaveforms = load_PSS_seq(base_path_PSS)

    q = Queue()

    print("start process")
    fshifts = [0, 15000, 30000, 45000]
    p1 = Process(target=processing_fshift, args=(fshifts[0], sampleRate, carrier, waveform, refWaveforms, q))    
    p2 = Process(target=processing_fshift, args=(fshifts[1], sampleRate, carrier, waveform, refWaveforms, q))
    p3 = Process(target=processing_fshift, args=(fshifts[2], sampleRate, carrier, waveform, refWaveforms, q))
    p4 = Process(target=processing_fshift, args=(fshifts[3], sampleRate, carrier, waveform, refWaveforms, q))
    p5 = Process(target=process_max_corr, args=(q,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    if(q.qsize() == len(fshifts)):
        p5.start()
        p5.join()
      



