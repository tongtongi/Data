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

def circ_r(vals, axis=0):
    alpha = np.array(vals, dtype='f8')
    # sum of cos & sin angles
    t = np.exp(1j * alpha)
    r = np.sum(t, axis=axis)
    # obtain length
    r = np.abs(r) / alpha.shape[axis]
    return r

def circ_mean(vals):
    x = np.sum(np.cos(vals))
    y = np.sum(np.sin(vals))

    return np.arctan2(y, x)


subfolders = glob.glob("100669/*/")

sessions = glob.glob("/home/tong/Desktop/stuff/*/")
for tl in sessions:
    num = int(re.search(r'/(\d*)/$', tl).group(1))
    for sf in glob.glob("/home/tong/Desktop/stuff/{}/*/".format(num)):
        print "Processing {}".format(sf)


        scroll = None

        try:


            scroll = pd.read_csv('{}ScrollEvent.csv'.format(sf), header=None,
                names=['Systime', 'BeginTime', 'CurrentTime', 'ActivityId', 'EventId', 'StartActionType',
                'StartX', 'StartY', 'StartPressure', 'StartSize', 'CurrentActionType', 'X',
                'Y', 'CurrentPressure', 'CurrentSize', 'DistanceX', 'DistanceY', 'PhoneOrientation'])

            scroll['Systime'] = scroll['Systime'].astype(float)

            # print signal.lfilter([1, -1], 1, [25.0, 50.0, 10.0, 15.0])
            scroll['xDisplacement'] = signal.lfilter([1, -1], 1, scroll['X'])
            scroll['xDisplacement'] = np.where(scroll['xDisplacement'] >= 100, 0, scroll['xDisplacement'])
            scroll['yDisplacement'] = signal.lfilter([1, -1], 1, scroll['Y'])
            scroll['yDisplacement'] = np.where(scroll['yDisplacement'] >= 100, 0, scroll['yDisplacement'])
            scroll['pairwiseTimeDiff'] = signal.lfilter([1, -1], 1, scroll['Systime'])
            scroll['pairwiseTimeDiff'] = np.where(scroll['pairwiseTimeDiff'] >= 100, 1, scroll['pairwiseTimeDiff'])
            scroll['pairwiseAngle'] = np.arctan2(scroll['yDisplacement'], scroll['xDisplacement'])
            scroll['pairwiseDisplacement'] = np.sqrt(pow(scroll['xDisplacement'], 2) + pow(scroll['yDisplacement'], 2))
            scroll['V'] = scroll['pairwiseDisplacement'] / scroll['pairwiseTimeDiff']
            scroll['A'] = signal.lfilter([1, -1], 1, scroll['V']) / scroll['pairwiseTimeDiff']

            result = scroll.groupby('EventId').agg({
                'StartX' : ['first'],
                'X' : ['last', ('maxdev', lambda x: (x-x.mean()).max()),
                    ('dev20', lambda x: (x-x.mean()).quantile(0.20)),
                    ('dev50', lambda x: (x-x.mean()).quantile(0.50)),
                    ('dev80', lambda x: (x-x.mean()).quantile(0.80))],
                'StartY': ['first'],
                'Y' : ['last', ('maxdev', lambda x: (x-x.mean()).max()),
                    ('dev20', lambda x: (x-x.mean()).quantile(0.20)),
                    ('dev50', lambda x: (x-x.mean()).quantile(0.50)),
                    ('dev80', lambda x: (x-x.mean()).quantile(0.80))],
                'V': [('pairwise20', lambda x: x.quantile(0.20)),
                    ('pairwise50', lambda x: x.quantile(0.50)),
                    ('pairwise80', lambda x: x.quantile(0.80)),
                    ('medianVelocityLastThree', lambda x: np.median(x.tail(3)))],
                'A': [('pairwise20', lambda x: x.quantile(0.20)),
                    ('pairwise50', lambda x: x.quantile(0.50)),
                    ('pairwise80', lambda x: x.quantile(0.80)),
                    ('averageAccFirstFive',
                        lambda x: np.median(x.head(5)) if x.size >= 5 else np.median(x))],
                'pairwiseDisplacement': [('lengthOfTrajectory', 'sum')],
                'Systime' : ['first', 'last'],
                'CurrentPressure': ['median'],
                'CurrentSize': ['median'],
                'PhoneOrientation': ['first']
            })

            result['distance'] = np.sqrt(pow(result['X']['last'] - result['StartX']['first'], 2) + pow(result['Y']['last'] - result['StartY']['first'], 2))
            result['directionOfEndtoEnfLine'] = np.arctan2((result['X']['last'] - result['StartX']['first']), (result['Y']['last'] - result['StartY']['first']))
            result['ratio'] = result['distance'] / result['pairwiseDisplacement']['lengthOfTrajectory']
            result['duration'] = result['Systime']['last'] - result['Systime']['first']
            result['averageVelocity'] = result['pairwiseDisplacement']['lengthOfTrajectory'] / result['duration']
            result['MeanResultantLength'] = circ_r(scroll['pairwiseAngle'])
            result['AverageDirectionEnsemble'] = circ_mean(scroll['pairwiseAngle'])

            # result['distance'] = np.sqrt(result['distance'])
            # print result
            # print result['StartX']['first']
            result.to_csv("{}Touchalitycs_out.csv".format(sf))

            # print scroll[:50]
        except IOError:
            print "Data file not found"
            continue