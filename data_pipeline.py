import sys
import model
import requests
import numpy as np
from time import sleep


def print_help():
    """Print help instructions on command line"""
    print('\n' + '\033[1m' + 'SYNOPSIS' + '\033[0m' + '\n\tdata_pipeline.py [-realtime] [-batch] [-help]')
    print('\n' + '\033[1m' + 'OPTIONS' + '\033[0m')
    print('\t' + '-realtime')
    print('\t  Runs the script in realtime mode.')
    print('\t  Thought for the real application.')
    print('\t  There will be data requests to the API periodicaly.')
    print('\n\t' + '-batch')
    print('\t  Runs the script in batch mode.')
    print('\t  It is thought for demo purposes.')
    print('\t  In this mode the data will fetched from the API just once.')
    print('\t  There won\'t be periodical data requests to the API.')
    print('\n\t' + '-help')
    print('\t  Prints the synopsis and descriptions for argument options.\n')


def get_hist_vital_sign(url):
    """Get the history of vital signs data of the patients from the given API.
    Also check if the API is responding as expected.

    Arguments:
    url (str): the url of the API endpoint.

    Returns:
    vital_sign_hist (list): a list of vital signs data of patients in JSON format.
    """
    resp_api = requests.get(url)
    vital_sign_hist = resp_api.json()['patient_list']
    return vital_sign_hist


if __name__ == '__main__':
    # Depending on called arguments...
    # ...the script runs in two operation modes: realtime or batch
    if len(sys.argv) == 1:  # If arguments are missing
        print('\ndata_pipeline.py: Missing arguments. See \'data_pipeline.py -help\'.\n')
    elif sys.argv[1] == '-realtime':  # realtime mode
        get_hist_vital_sign('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
    elif sys.argv[1] == '-batch':  # batch mode for demo purposes
        # TBD
        pass
    elif sys.argv[1] == '-help':
        print_help()  # prints help on the command line
    else:  # unexpected arguments given
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


