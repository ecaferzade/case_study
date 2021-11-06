import sys
import model
import requests
import numpy as np
import re
import time


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


def get_vital_sign_hist(url):
    """Get the history of vital signs data of the patients from the given API.

       Arguments:
       url (str): the url of the API endpoint.

       Returns:
       vital_sign_history (list): a list of vital signs data of patients in JSON format.
    """
    resp_api = requests.get(url)
    print('\nThe status code of the api response is: \n', resp_api.status_code)
    if not (200 <= resp_api.status_code < 300):  # Check if HTTP status code is OK
        print("Problem: status code of the response", resp_api.status_code)
    vital_sign_history = resp_api.json()['patient_list']
    if not vital_sign_history:  # If vital_sign_history is empty
        print('The API didn\'t respond with content.')
    return vital_sign_history


def conv_dict_to_list(pat_dict):
    pat_l = list(pat_dict.values())
    return pat_l


def extract_nmbr_from_str(vital_val_str):
    vital_val_floats = re.findall(r'[-+]?\d*\.\d+|\d+', vital_val_str)
    return vital_val_floats


if __name__ == '__main__':
    # Depending on called arguments...
    # ...the script runs in two operation modes: realtime or batch
    if len(sys.argv) == 1:  # If arguments are missing
        print('\ndata_pipeline.py: Missing arguments. See \'data_pipeline.py -help\'.\n')
    elif sys.argv[1] == '-realtime':  # realtime mode
        # TBD
        pass
    elif sys.argv[1] == '-batch':  # batch mode for demo purposes
        pat_list = []
        for _ in range(10):
            vital_sign_hist = get_vital_sign_hist('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            if not vital_sign_hist:  # If API response is empty
                pass
            else:  # If the API responded with content
                for patience in vital_sign_hist:
                    pat_info = conv_dict_to_list(patience)
                    vital_val = extract_nmbr_from_str(pat_info[1])
                    pat_info = pat_info[0:1] + vital_val
                    pat_list.append(pat_info)
        try:
            data = np.array(pat_list)
            X = data[:, 1:-1].astype(float)  # get rid off pat_id & timestamp with index slicing
            model = model.ICUZen()
            predictions = model.predict(X)
            data = np.column_stack((data, predictions))
            data = np.unique(data, axis=0)
            file = open('collected_data.txt', 'w')
            np.savetxt(file, data, delimiter=',', fmt="%s")
            file.close()
        except IndexError:
            print('None of the GET requests to the API resulted with data.')
    elif sys.argv[1] == '-help':  # If help is needed
        print_help()  # prints help on the command line
    else:  # unexpected arguments given
        print('\ndata_pipeline.py: Unexpected argument \'{}\'.'
              ' Please run with \'-help\' to see the expected arguments.\n'.format(sys.argv[1]))
