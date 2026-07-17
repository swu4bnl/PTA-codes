import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from pathlib import Path, PureWindowsPath
import palettable as pltt # https://jiffyclub.github.io/palettable/
import glob
import time
from larch.io import read_ascii, read_athena
from scipy.signal import find_peaks


from tiled.client import from_uri
client = from_uri('https://tiled.nsls2.bnl.gov')
# dbBMM = client['bmm']['raw']

dbBMM = from_uri("https://tiled.nsls2.bnl.gov/api/v1/metadata/bmm/raw", api_key='1578614050ded8f5c9503ec378ebfc41679a1510d375540ce655cc559d8400dbd2dea288')

UID_LIST = []


def BMM_analysis_TI(scan_id=-1, energy_range = None, dbBMM = dbBMM, client = client, verbosity=0):
    


    DISTANCE = 15   # Distance is the minimum distance between peaks
    PROMINENCE = 10 # Prominence is the minimum height of peaks
    
    # Assign energy and fluorescence counts as x and y
    number_of_detector = 7
    fluorescence_total_counts = 0
    data = dbBMM[scan_id]["primary"]["data"]
    # pprint(dbBMM[scan_id].metadata['start'])
    # pprint(dbBMM[scan_id].metadata['start']['XDI'])
    element = dbBMM[scan_id].metadata['start']['XDI']['_user']['element']   # Need to confirm
    print(element)
    for index in range(1, 1 + number_of_detector):
        fluorescence_detector = str(f"{element}{index}")
        fluorescence_counts = np.array(data[fluorescence_detector])
        i0 = data["I0"]
        fluorescence_total_counts += fluorescence_counts / i0

    x = np.array(data["dcm_energy"])
    y = fluorescence_total_counts

    if energy_range == None:
        energy_range = (np.array(data["dcm_energy"])[0], np.array(data["dcm_energy"])[-1])
    INDEX_RANGE = x.searchsorted(energy_range)

    # Find peaks
    peaks, _ = find_peaks(y[INDEX_RANGE[0]:INDEX_RANGE[1]],
                          distance=DISTANCE, prominence=PROMINENCE) # Distance is the minimum distance between peaks
    print(peaks)
    
    # If no peak is found, assign -1
    # if len(peaks) == 0:
    #     peaks = [-1]
    # peak_position = x[INDEX_RANGE[0]:INDEX_RANGE[1]][peaks][0]
    # print(peak_position)

    ratio = y[INDEX_RANGE[0]:INDEX_RANGE[1]][peaks][0]/y[INDEX_RANGE[0]:INDEX_RANGE[1]][peaks][1]

    if verbosity>=3:
        # ------------------------------------------------------
        fig, ax = plt.subplots(1, 1, figsize=(6, 7.5))
        # Plot the absorption spectrum
        plt.plot(x[INDEX_RANGE[0]:INDEX_RANGE[1]],
                 y[INDEX_RANGE[0]:INDEX_RANGE[1]],
                 color='black', linewidth=2, label='Absorption')
        # Label the peaks
        plt.plot(x[INDEX_RANGE[0]:INDEX_RANGE[1]][peaks],
                 y[INDEX_RANGE[0]:INDEX_RANGE[1]][peaks],
                 'x', color='red', label='Peaks', markersize=10)
        plt.legend()
        plt.show()
    # ------------------------------------------------------

    # output 
    scan_id = dbBMM[scan_id].metadata['start']['scan_id']
    uid = dbBMM[scan_id].metadata['start']['uid']

    mt = dbBMM[scan_id].metadata['start']['XDI']['_comment']
    mt_sample = mt[0].split(',')[0].split('= ')[-1]
    mt_distance = mt[0].split(',')[1].split('= ')[-1]
    mt_time = mt[0].split(',')[2].split('= ')[-1]

    mt_distance = float(mt_distance)
    mt_time = float(mt_time)

    results = {}
    results['scan_id'] = scan_id
    results['uid'] = uid
    results['x_BMM'] = mt_distance
    results['clock_BMM'] = mt_time
    results['results_BMM'] = ratio
    results['sample_BMM'] = mt_sample
    results['measured'] = True
    results['analyzed'] = True
    #package it in gpCAM format
    #save to npy
    
    folder = '/nsls2/data3/cms/legacy/xf11bm/data/2025_1/KChen-Wiegart6/BMM/'
    np.save(folder+str(scan_id)+'_'+str(mt_time)+'_'+str(mt_distance), results)    
    print([results])
    return [results]



def check_xafs_status(scan_id=-1, dbBMM=dbBMM):
    plan_name = dbBMM[scan_id].metadata['start']['plan_name'] # check if 'xafs' is in the name, otherwise it could be camera data
    if 'xafs fluorescence' in plan_name:           # count xafs_metadata XRF if that is a XRF data
        return True
    else:
        return False

def check_complete_status(scan_id=-1, dbBMM=dbBMM):
    if dbBMM[scan_id].metadata['stop'] == None:        # check if the scan is done, otherwise it would show 'None'
        return False
    else:
        return True

def check_uid(scan_history, scan_id=-1, dbBMM=dbBMM):
    scan_uid = dbBMM[scan_id].metadata['start']['uid']     # scan uid, we need to check the history if the uid is in the list
    if scan_uid in scan_history:
        return False
    else:
        scan_history.append(scan_uid)
        return True

# check BMM status and sleep
def check_BMM_status(scan_id=-1, dbBMM=dbBMM):
    data = dbBMM[scan_id]
    if check_xafs_status(scan_id) and check_complete_status(scan_id):
        if check_uid(UID_LIST, scan_id):  # If the scan is done, add the scan to the history
            return True
        else:
            return False
    else:
        return False

# pass BMM_analysis results to gpCAM
def pack_BMM_analysis(scan_id=-1, energy_range=(4950, 5010)):

    ratio, mt_sample, mt_distance, mt_time = BMM_analysis_Ti(scan_id=scan_id, energy_range = energy_range)
    
    #TODO
    results = {}
    results['x_BMM'] = mt_distance
    results['clock_BMM'] = mt_time
    results['results_BMM'] = ratio
    results['sample_BMM'] = mt_sample
    results['measured'] = True
    results['analyzed'] = True
    #package it in gpCAM format
    #save to npy
    
    folder = '/nsls2/data3/cms/legacy/xf11bm/data/2025_1/KChen-Wiegart6/BMM/'
    np.save(folder+str(mt_time)+mt_distance, results)    
    print(results)
    return results

# run everythin in while loop forever

def run_BMM(scan_id, wait_time=30, energy_range=(4950, 5010), verbosity=0):


    if check_BMM_status():
        print('check status')
        # ss = BMM_analysis(scan_id=scan_id)
        # ss = BMM_analysis_Ti(scan_id=scan_id, energy_range = energy_range)
        ss = BMM_analysis_TI(scan_id=scan_id, energy_range = energy_range, verbosity=verbosity)
        q.publish(ss)
        return ss
    else:
        if check_xafs_status(scan_id=scan_id):
            print(dbBMM[scan_id].metadata['start']['plan_name'])
            try:
                print(f'Scanning to {dbBMM[scan_id]["primary"]["data"]["dcm_energy"][-1]:.1f} eV')
            except KeyError:
                print('Scan starts!')
                pass

        print('sleep')
        time.sleep(wait_time)








####################
from CustomS3BMM import Queue_analyze
q = Queue_analyze()

# while True: # The loop that waits for new instructions...
    
#     # Check BMM, wait for new data. Once you get new data:
#     # Get data from BMM
#     # Do custom analysis, put data into into the right format
#     # data = [ {...} ]
#     data = run_BMM(-1, verbosity=0)
#     # q.publish(data) # Send new analysis results to gpCAM