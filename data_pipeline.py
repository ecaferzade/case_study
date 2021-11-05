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


def conv_vital_to_array(vital_sign_history):
    """Create the vital sign matrix (np.array) out of vital sign history list
       to feed it in the ICU model: Extract the vital sign values from string
       using regular expressions, convert them in floats
       and make a numpy array out of it.

       Arguments:
       vital_sign_history (list): This is a list of dictionaries where each dict represents
       a patients data.

       Returns:
       vital_array (np.array) : Vital signs as a MxN matrix, where M in the number of patients
       and N number of vital signs.
    """
    temp = []  # temp list used for list->np.array transition
    for patient in vital_sign_history:
        vit_val = re.findall(r'[-+]?\d*\.\d+|\d+', patient['vital_signs'])
        temp.append([float(i) for i in vit_val])  # Collect all floats in this list
    vital_arr = np.array(temp)  # Make an np.array out of the list
    return vital_arr


if __name__ == '__main__':
    # Depending on called arguments...
    # ...the script runs in two operation modes: realtime or batch
    if len(sys.argv) == 1:  # If arguments are missing
        print('\ndata_pipeline.py: Missing arguments. See \'data_pipeline.py -help\'.\n')
    elif sys.argv[1] == '-realtime':  # realtime mode
        # TBD
        pass
    elif sys.argv[1] == '-batch':  # batch mode for demo purposes
        model = model.ICUZen()
        file = open('xyz.txt', 'w')
        data = np.array([['pat_id', 'body_temp', 'blood_pres_sys', 'blood_pres_dia',
                         'heart_rate', 'resp_rate', 'time_stmp', 'predic']])
        while True:
            vital_sign_hist = get_vital_sign_hist('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            if not vital_sign_hist:  # If vital_sign_history is empty
                pass
            else:  # If the API responded with content
                pat_id = np.array([[x['patient_id'] for x in vital_sign_hist]])  # patient ids
                vital_array = conv_vital_to_array(vital_sign_hist)  # input prep for predict function
                predictions = model.predict(vital_array[:, :-1])  # timestamp col is not expected by predict function
                new_dat = np.column_stack((pat_id.T, vital_array, predictions))
                data = np.unique(np.row_stack((data, new_dat)), axis=0)
                np.savetxt(file, data, delimiter=',', fmt="%s")
                break

            print('Saving completed.')

    elif sys.argv[1] == '-help':  # If help is needed
        print_help()  # prints help on the command line
    else:  # unexpected arguments given
        print('\ndata_pipeline.py: Unexpected argument \'{}\'.'
              ' Please run with \'-help\' to see the expected arguments.\n'.format(sys.argv[1]))
