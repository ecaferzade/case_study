# Idalab Data Engineer Case-Study: Data Pipeline
This README gives an overview of data_pipeline.py scripts design and functionality.

## Description
This python script connects with the MensSana_ICU_API and collects data of ICU patients.
The data consists of a unique patient id and medical data such as body temperature, heart rate, etc. for each patient in intensive care unit(s).
After the collection, data is given to a ML model to predict based on medical data wether an alarm should be thrown or not.
The program outputs a text file which contains collected data and corresponding predictions of the model. 

## Operating Modes
The script can be run in two modes: realtime and demo.
These two modes differ in the stopping criterion for data collection.
In the realtime mode, data will be collected until the user presses the ENTER and thus terminates the program. This gives one the flexibility of not having 
to determine the number of data request iterations beforehand. This mode is thought as a draft for future real application of the data pipeline, where
real patients data flow continuously.
On the other hand, demo mode is thought for demo purposes. Here the user gives the desired number of data request iterations as argument to the program. After given number of iterations are completed, the program terminates.
In both modes, the program outputs the results (collected data in an organised form and the predictions) and save them locally.

## Technical Details
#### Functions
The functions defined in the program fall in two major categories: 
1) The ones used for communication with the user, i.e printing on the prompt. These are pretty straight forward and won't be discussed here.
2) The other ones are used to prepare the output:
  * get_pat_hist(), conv_dict_to_list(), extract_nmbr_from_str() are functions for to collect data from API, prepare the data as input for the ML model respectively.
  * make_pred() and save_results() are responsible for prediction making based on the collected data and saving of it.
For details about the functions please refer to the docstrings.
#### Dependencies

* numpy
* model.py
## Running the program
#### Synopsis
Usage : `data_pipeline.py {-realtime | -demo <req_nr> | -help} [<filename>]`.
#### Options
* -realtime :
	  Runs the script in realtime mode.
	  Thought for the real application.
	  The script continues collecting data until ENTER is pressed by the user.
* -demo req_nr :
	  Runs the script in demo mode.
	  Thought for demo purposes.
	  req_nr is the desired number of GET requests to collect the data and has to be specified by the user.
	  The script terminates when the req_nr GET requests are made to the API.
* -help :
	  Prints the description, synopsis and  details for argument options.
*  filename (optional) :
	  Desired name of the output file that contains the data & predictions (= results).
	  Default value: results.

To see the detailed usage message you can also run: **`python3 data_pipeline.py -help`** on your terminal.
