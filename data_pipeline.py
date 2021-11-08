import sys
import model
import requests
import numpy as np
import re
import logging
import select


def print_help():
    """
    Print help instructions on command line
    :return:
    """
    logging.info('\n' + '\033[1m' + 'SYNOPSIS' + '\033[0m' + '\n\tdata_pipeline.py {-realtime | -batch -req_nr} [-help]')
    logging.info('\n' + '\033[1m' + 'OPTIONS' + '\033[0m')
    logging.info('\t' + '-realtime')
    logging.info('\t  Runs the script in realtime mode.')
    logging.info('\t  Thought for the real application.')
    logging.info('\t  There will be data requests to the API periodicaly.')
    logging.info('\t  The script continues collecting data until ENTER is pressed.')
    logging.info('\n\t' + '-demo -req_nr')
    logging.info('\t  Runs the script in demo mode.')
    logging.info('\t  Thought for demo purposes.')
    logging.info('\t  There will be data requests to the API periodicaly.')
    logging.info('\t  req_nr is the desired number of GET requests to collect the data.')
    logging.info('\t  The script terminates when the req_nr GET requests are made to the API.')
    logging.info('\n\t' + '-help')
    logging.info('\t  Prints the synopsis and descriptions for argument options.\n')




def get_vital_sign_hist(url):
    """
    Get the history of vital signs data of the patients from the given API.

       Arguments:
       url (str): the url of the API endpoint.

       Returns:
       vital_sign_history (list): a list of vital signs data of patients in JSON format.

    :param url:
    :return:
    """
    resp_api = requests.get(url)
    if not (200 <= resp_api.status_code < 300):  # Check if HTTP status code is OK
        logging.info("Problem: status code of the response", resp_api.status_code)
    vital_sign_history = resp_api.json()['patient_list']
    return vital_sign_history


def conv_dict_to_list(pat_dict):
    """

    :param pat_dict:
    :return:
    """
    pat_l = list(pat_dict.values())
    return pat_l


def extract_nmbr_from_str(vital_val_str):
    """

    :param vital_val_str:
    :return:
    """
    vital_val_floats = re.findall(r'[-+]?\d*\.\d+|\d+', vital_val_str)
    return vital_val_floats


def make_pred(patience_list, mdl, filename=):
    """

    :param patience_list:
    :param mdl:
    :param filename:
    :return:
    """
    data = np.array(patience_list)
    x = data[:, 1:-1].astype(float)  # prepare data as input for the model
    mdl = mdl
    predictions = mdl.predict(x)
    data = np.column_stack((data, predictions))  # add corresponding predictions as col to pat info
    data = np.unique(data, axis=0)  # filter redundant data
    file = open('.txt', 'w')
    file_header = 'pat_id, body_temp, blood_pres_sys, blood_pres_dia, heart_rate, resp_rate, time_stmp, predic'
    np.savetxt(file, data, delimiter='\t', header=file_header, fmt="%s")  # save the data locally.
    file.close()


if __name__ == '__main__':
    # Depending on given arguments...
    # ...the script runs in two operation modes: realtime or demo
    logging.basicConfig(format='%(message)s', level=logging.INFO)  # log config for future loggings
    if len(sys.argv) == 1:  # If arguments are missing
        logging.info('\ndata_pipeline.py: Missing arguments. See \'data_pipeline.py -help\'.\n')
    elif (len(sys.argv)) == 2 and (sys.argv[1] == '-realtime'):  # realtime mode
        pat_list = []
        logging.info('Collecting data...')
        logging.info('Press ENTER to save data and quit.')
        while True:
            vital_sign_hist = get_vital_sign_hist('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            for patience in vital_sign_hist:  # for each dict in a list of dicts do:
                pat_info = conv_dict_to_list(patience)  # convert each dict to a list
                vital_val = extract_nmbr_from_str(pat_info[1])  # extract vital values from a single string
                pat_info = pat_info[0:1] + vital_val  # new pat. info where every vital val is a discrete str.
                pat_list.append(pat_info)  # add this formed pat. info to the big list
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:  # if ENTER is pressed (on UNIX):
                try:
                    make_pred(pat_list, model.ICUZen())
                except IndexError:  # API didn't respond with content.
                    logging.info('None of the GET requests to the API resulted with data.')
                    logging.info('Please try again.')
                finally:
                    break
    elif (len(sys.argv) == 3) and (sys.argv[1] == '-batch') and (sys.argv[2].isdigit()):  # batch mode for demo purposes
        pat_list = []
        for _ in range(int(sys.argv[2])):  # do sys.argv[2]==req_nr GET requests
            vital_sign_hist = get_vital_sign_hist('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            for patience in vital_sign_hist:  # for each dict in a list of dicts do:
                pat_info = conv_dict_to_list(patience)  # convert each dict to a list
                vital_val = extract_nmbr_from_str(pat_info[1])  # extract vital values from a single string
                pat_info = pat_info[0:1] + vital_val  # new pat. info where every vital val is a discrete str.
                pat_list.append(pat_info)  # add this formed pat. info to the big list
        try:
            make_pred(pat_list, model.ICUZen())
        except IndexError:
            logging.info('None of the GET requests to the API resulted with data.')
    elif sys.argv[1] == '-help':  # If help is needed
        print_help()  # prints help on the command line
    else:  # unexpected arguments given
        logging.info('\ndata_pipeline.py: Unexpected argument \'{}\'.'
              ' Please run with \'-help\' to see the expected arguments.\n'.format(' '.join(sys.argv[1:])))
