from math import acos
from math import isnan
from math import sqrt
from math import pi
from math import hypot
from scipy import signal
from collections import OrderedDict
import pandas as pd
import numpy as np
import glob, os
import time
import re
import sys


subfolders = glob.glob("100669/*/")

sessions = glob.glob("/home/tong/Desktop/stuff/*/")
for tl in sessions:
    num = int(re.search(r'/(\d*)/$', tl).group(1))
    for sf in glob.glob("/home/tong/Desktop/stuff/{}/*/".format(num)):
        print "Processing {}".format(sf)

        acc = None
        gyro = None
        magneto = None

        touch = None
        scroll = None
        stroke = None
        try:
            # print ('{}Accelerometer.csv'.format(sf))
            # acc = pd.read_csv('{}Accelerometer.csv'.format(sf), header=None,
            #     names=['Systime', 'EventTime', 'ActivityId', 'X', 'Y', 'Z', 'PhoneOrientation'])
            # gyro = pd.read_csv('{}Gyroscope.csv'.format(sf), header=None,
            #     names=['Systime', 'EventTime', 'ActivityId', 'X', 'Y', 'Z', 'PhoneOrientation'])
            # magneto = pd.read_csv('{}Magnetometer.csv'.format(sf), header=None,
            #     names=['Systime', 'EventTime', 'ActivityId', 'X', 'Y', 'Z', 'PhoneOrientation'])

            # touch = pd.read_csv('{}TouchEvent.csv'.format(sf), header=None,
            #     names=['Systime', 'EventId', 'ActivityId', 'PointerCount', 'PointerID',
            #     'ActionID', 'X', 'Y', 'Pressure', 'ContactSize', 'PhoneOrientation'])



            scroll = pd.read_csv('{}ScrollEvent.csv'.format(sf), header=None,
                names=['Systime', 'BeginTime', 'CurrentTime', 'ActivityId', 'EventId', 'StartActionType',
                'StartX', 'StartY', 'StartPressure', 'StartSize', 'CurrentActionType', 'X',
                'Y', 'CurrentPressure', 'CurrentSize', 'DistanceX', 'DistanceY', 'PhoneOrientation'])


            scroll['Systime'] = scroll['Systime'].astype(float)

            print signal.lfilter([1, -1], 1, [25.0, 50.0, 10.0, 15.0])
            scroll['xDisplacement'] = signal.lfilter([1, -1], 1, scroll['X'])
            scroll['xDisplacement'] = np.where(scroll['xDisplacement'] >= 100, 0, scroll['xDisplacement'])
            scroll['yDisplacement'] = signal.lfilter([1, -1], 1, scroll['Y'])
            scroll['yDisplacement'] = np.where(scroll['yDisplacement'] >= 100, 0, scroll['yDisplacement'])
            scroll['pairwiseTimeDiff'] = signal.lfilter([1, -1], 1, scroll['Systime'])
            # scroll['pairwiseTimeDiff'] = np.where(scroll['pairwiseTimeDiff'] >= 100, 1, scroll['pairwiseTimeDiff'])
            scroll['pairwiseAngle'] = np.arctan2(scroll['yDisplacement'], scroll['xDisplacement'])
            scroll['pairwiseDisplacement'] = np.sqrt(pow( scroll['xDisplacement'],2) + pow( scroll['yDisplacement'],2))
            scroll['V'] = scroll['pairwiseDisplacement'] / scroll['pairwiseTimeDiff']
            scroll['A'] = signal.lfilter([1, -1], 1, scroll['V']) / scroll['pairwiseTimeDiff']


            # print scroll['pairwiseTimeDiff'].astype(int)
            #
            # sys.exit(0)



            result = scroll.groupby('EventId').agg({
                'StartX' : ['first'],
                'X' : ['last'],
                'StartY': ['first'],
                'Y': ['last'],
                'V': [('pairwise20', lambda x: x.quantile(0.20)), ('pairwise50', lambda x: x.quantile(0.50)), ('pairwise80', lambda x: x.quantile(0.80)), ('medianVelocityLastThree', lambda x: np.mean(x.tail(3)))],
                'A': [('pairwise20', lambda x: x.quantile(0.20)), ('pairwise50', lambda x: x.quantile(0.50)), ('pairwise80', lambda x: x.quantile(0.80)),('averageAccFirstFive',
                                                                                                               lambda x: np.median(x.head(5)) if x.size >=5 else np.median(x))],
                'pairwiseDisplacement': [('lengthOfTrajectory', 'sum')],
                'Systime' : ['first', 'last']

            })

            result['distance'] = np.sqrt(pow(result['X']['last'] - result['StartX']['first'], 2) + pow(result['Y']['last'] - result['StartY']['first'], 2))
            result['directionOfEndtoEnfLine'] = np.arctan2((result['X']['last'] - result['StartX']['first']), (result['Y']['last'] - result['StartY']['first']))
            result['ratio'] = result['distance'] / result['pairwiseDisplacement']['lengthOfTrajectory']
            result['duration'] = result['Systime']['last'] - result['Systime']['first']
            result['averageVelocity'] = result['pairwiseDisplacement']['lengthOfTrajectory'] / result['duration']

            # result['distance'] = np.sqrt(result['distance'])
            result.to_csv("{}Touchalitycs_out.csv".format(sf))
            # print result['StartX']['first']


            # print scroll[:50]
        except IOError:
            print "Data file not found"
            continue