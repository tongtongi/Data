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


sessions = glob.glob("/home/tong/Desktop/stuff/*/")
for tl in sessions:
    num = int(re.search(r'/(\d*)/$', tl).group(1))
    data = pd.DataFrame()
    for sf in glob.glob("/home/tong/Desktop/stuff/{}/*/".format(num)):
        print "Processing {}".format(sf)
        try:
            accOut = None
            gyroOut = None
            magnetoOut = None
            safeguardOut = None
            touchalitycsOut = None

            safeguardOut = pd.read_csv('{}SafeGuard_out.csv'.format(sf), header=[0, 1])

            safeguardOut = safeguardOut.add_prefix('SAFEG_')
            touchalitycsOut = pd.read_csv('{}Touchalitycs_out.csv'.format(sf), header=[0, 1])
            touchalitycsOut = touchalitycsOut.add_prefix('TOUCHALITYCS_')
            accOut = pd.read_csv('{}acc_scroll_out.csv'.format(sf), header=[0, 1])
            accOut = accOut.add_prefix('ACC_')
            accOut = accOut.rename(columns={'ACC_UserId': 'USER_ID'})
            gyroOut = pd.read_csv('{}gyro_scroll_out.csv'.format(sf), header=[0, 1])
            gyroOut.drop('UserId', axis=1, inplace=True)
            gyroOut = gyroOut.add_prefix('GYRO_')
            magnetoOut = pd.read_csv('{}magneto_scroll_out.csv'.format(sf), header=[0, 1])
            magnetoOut.drop('UserId', axis=1, inplace=True)
            magnetoOut = magnetoOut.add_prefix('MAGNETO_')

            df_concat = pd.concat([accOut, gyroOut, magnetoOut, touchalitycsOut, safeguardOut], axis=1)
            # df_concat.to_csv("{}Scroll_Merged.csv".format(sf))

        except IOError:
            print "Data file not found"
            continue

        data = pd.concat([data, df_concat], axis=0, levels=1, ignore_index=True)
    data.to_csv("{}Scroll_ALL.csv".format(tl))