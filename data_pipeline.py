import sys
import model
import requests
import numpy as np
import re
import logging
import select


def print_help():
    """
    Print usage message (incl. description, synopsis and options) on command line
    :return: -
    """
    logging.info('\n' + '\033[1m' + 'DESCRIPTION' + '\033[0m')
    logging.info('\t This python script connects with the MensSana_ICU_API and collects data of ICU patients.')
    logging.info('\t After the collection, data is given to a ML model to predict wether an alarm should be thrown or not.')
    logging.info('\t From API collected data and predictions based on it are in the end saved as a .txt file.')
    logging.info('\t The script can be run in two modes: realtime and demo')
    logging.info('\t These two modes differ in the stopping criterion for data collection.')
    logging.info('\n' + '\033[1m' + 'SYNOPSIS' + '\033[0m' + '\n\tdata_pipeline.py [-realtime | -demo req_nr | -help] [filename]')
    logging.info('\n' + '\033[1m' + 'OPTIONS' + '\033[0m')
    logging.info('\t' + '-realtime')
    logging.info('\t  Runs the script in realtime mode.')
    logging.info('\t  Thought for the real application.')
    logging.info('\t  The script continues collecting data until ENTER is pressed by the user.')
    logging.info('\n\t' + '-demo req_nr')
    logging.info('\t  Runs the script in demo mode.')
    logging.info('\t  Thought for demo purposes.')
    logging.info('\t  req_nr is the desired number of GET requests to collect the data.')
    logging.info('\t  The script terminates when the req_nr GET requests are made to the API.')
    logging.info('\n\t' + '-help')
    logging.info('\t  Prints the descriptions, synopsis and  details for argument options.')
    logging.info('\n\t' + 'filename ' + '\x1B[3m' + '(optional)' + '\x1B[0m')
    logging.info('\t  With this optional argument user can name the output file that contains the data & predictions.')
    logging.info('\t  Default value: results.\n')


def print_unexp_arg():
    """
    Print instructions on command line when unexpected arguments are given to the program.
    :return: -
    """
    logging.info('\ndata_pipeline.py: Unexpected argument \'{}\'.'
                 ' Please run with \'-help\' to see the expected arguments.\n'.format(' '.join(sys.argv[1:])))


def print_miss_arg():
    """
    Print instructions on command line when unexpected arguments are given to the program.
    :return: -
    """
    logging.info('\ndata_pipeline.py: Missing arguments. See \'data_pipeline.py -help\'.\n')


def get_vital_sign_hist(url):
    """
    Get the history of vital signs data of the patients from the given API.
    :param url: (str) the url of the API endpoint
    :return vital_sign_history: (list) vital signs list, where each element is a dictionary and represents a patient.
    """
    resp_api = requests.get(url)
    if not (200 <= resp_api.status_code < 300):  # Check if HTTP status code is OK
        logging.info("Problem: status code of the response", resp_api.status_code)
    vital_sign_history = resp_api.json()['patient_list']
    return vital_sign_history


def conv_dict_to_list(pat_dict):
    """
    Convert each patients dictionary to a list for further processing.
    :param pat_dict: (dict) patient info in dictionary form.
    :return pat_l: (list) patient info in list form.
    """
    pat_l = list(pat_dict.values())
    return pat_l


def extract_nmbr_from_str(vital_val_str):
    """
    Extract numbers from a string using regular expressions.
    :param vital_val_str: (str) This string contains all vital sign values like body temperature etc.
    :return vital_values: (list) The elements of this list are vital sign values in string format.
    """
    vital_values = re.findall(r'[-+]?\d*\.\d+|\d+', vital_val_str)
    return vital_values


def make_pred(patience_list, mdl):
    """
    Prepare collected data for giving it as model input: Convert it to a np.array with datatype floats.
    Filter redundant data and by the model not expected features.
    :param patience_list: (list) Consists of all collected patient info
    :param mdl: (model.ICUZen) ML model used for the predictions.
    :return reslt: (np.array) This array contains all unique patient info and corresponding predictions and
                                forms therefore the desired results.
    """
    data = np.array(patience_list)
    data = np.unique(data, axis=0)  # filter redundant data
    x = data[:, 1:-1].astype(float)  # prepare data as input for the model
    mdl = mdl
    predictions = mdl.predict(x)
    reslt = np.column_stack((data, predictions))  # add corresponding predictions as col to pat info
    return reslt


def save_results(reslt, filename='results'):
    """
    Save the resulting data, i.e the patient information and corresponding prediction of the ML model to a .txt file.
    :param reslt: (np.array) resulting data to save
    :param filename: (str) Optional argument to name the file to be saved.
    :return: -
    """
    file = open(filename + '.txt', 'w')
    file_header = 'pat_id, body_temp, blood_pres_sys, blood_pres_dia, heart_rate, resp_rate, time_stmp, predic'
    np.savetxt(file, reslt, delimiter='\t', header=file_header, fmt="%s")  # save the data locally.
    file.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.INFO)  # log config for future loggings
    if len(sys.argv) == 1:  # If arguments are missing
        print_miss_arg()
    elif sys.argv[1] == '-realtime':  # realtime mode chosen.
        if len(sys.argv) > 3:  # if too many args are given.
            print_unexp_arg()
            exit()
        pat_list = []
        logging.info('Collecting data...')
        logging.info('To quit with saving the collected data press ENTER.')
        while True:
            vital_sign_hist = get_vital_sign_hist('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            for patience in vital_sign_hist:  # for each dict in a list of dicts do:
                pat_info = conv_dict_to_list(patience)  # convert each dict to a list
                vital_val = extract_nmbr_from_str(pat_info[1])  # extract vital values from a single string
                pat_info = pat_info[0:1] + vital_val  # new pat. info where every vital val is a discrete str.
                pat_list.append(pat_info)  # add this formed pat. info to the big list
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:  # if ENTER is pressed (on UNIX):
                try:
                    if len(sys.argv) == 3:  # if desired file name is provided.
                        results = make_pred(pat_list, model.ICUZen())
                        save_results(results, sys.argv[2])
                    else:  # if not proceed with default file name.
                        results = make_pred(pat_list, model.ICUZen())
                        save_results(results)
                    logging.info('\nData collection and model prediction completed. Results are saved.')
                except IndexError:  # API didn't respond with content.
                    logging.info('None of the GET requests to the API resulted with data.')
                    logging.info('Please try again.')
                finally:
                    break
    elif (len(sys.argv) == 2) and (sys.argv[1] == '-demo'):
        print_miss_arg()
    elif (sys.argv[1] == '-demo') and (sys.argv[2].isdigit()):  # demo mode
        if len(sys.argv) > 4:  # if too many args are given.
            print_unexp_arg()
            exit()
        pat_list = []
        logging.info('Collecting data...')
        for request in range(int(sys.argv[2])):  # do sys.argv[2]==req_nr GET requests
            vital_sign_hist = get_vital_sign_hist('https://idalab-icu.ew.r.appspot.com/history_vital_signs')
            sys.stdout.write("\rNumber of made requests so far: {}".format(request+1))
            sys.stdout.flush()
            for patience in vital_sign_hist:  # for each dict in a list of dicts do:
                pat_info = conv_dict_to_list(patience)  # convert each dict to a list
                vital_val = extract_nmbr_from_str(pat_info[1])  # extract vital values from a single string
                pat_info = pat_info[0:1] + vital_val  # new pat. info where every vital val is a discrete str.
                pat_list.append(pat_info)  # add this formed pat. info to the big list
        try:
            if len(sys.argv) == 4:  # if desired file name is provided.
                results = make_pred(pat_list, model.ICUZen())
                save_results(results, sys.argv[3])
            else:  # if not proceed with default file name.
                results = make_pred(pat_list, model.ICUZen())
                save_results(results)
            logging.info('\nData collection and model prediction completed. Results are saved.')
        except IndexError:
            logging.info('None of the GET requests to the API resulted with data.')
            logging.info('Please try again.')
    elif sys.argv[1] == '-help':  # If help is needed
        print_help()  # prints help on the command line
    else:  # unexpected arguments given
        print_unexp_arg()
