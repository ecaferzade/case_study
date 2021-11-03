import sys
import model
import requests
import numpy as np
from time import sleep


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('\ndata_pipeline.py: Missing arguments. See \'data_pipeline.py -help\'.\n')
    elif sys.argv[1] == '-help':
        print('\n'+'\033[1m'+'SYNOPSIS'+'\033[0m'+'\n\tdata_pipeline.py [-realtime] [-batch] [-help]')
        print('\n'+'\033[1m'+'OPTIONS'+'\033[0m')
        print('\t' + '-realtime')
        print('\t  Runs the script in realtime mode.')
        print('\t  Thought for the real application.')
        print('\t  There will be data requests to the API periodicaly.')
        print('\n\t' + '-batch')
        print('\t  Runs the script in batch mode.')
        print('\t  It is thought for demo purposes.')
        print('\t  In this mode the data will fetched from the API just once.')
        print('\t  There won\'t be periodical data requests to the API.')
        print('\n\t'+'-help')
        print('\t  Prints the synopsis and descriptions for argument options.\n')
    elif sys.argv[1] == '-batch':
        print('batch mode activated.')
    elif sys.argv[1] == '-realtime':
        r_api1 = requests.get('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
        d1 = r_api1.json()
        while True:
            #sleep(0.0001)
            r_api2 = requests.get('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            print(r_api2.status_code)
            d2 = r_api1.json()
            print(d1 == d2)
    else:
        print('\ndata_pipeline.py: Unexpected argument \'{}\'. Please run with \'-help\' to see the expected arguments.\n'.format(sys.argv[1]))





    """
    l = []
    for t in d['vital_signs'].split():
        try:
            l.append(float(t))
        except ValueError:
            pass
    array = np.array(l[:-1], ndmin=2)
    print(array.shape)
    icu = model.ICUZen()
    alarm = icu.predict(array)
    print(alarm)
    """


