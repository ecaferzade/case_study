#### Idalab Data Engineer Case-Study: Data Pipeline
This README gives an overview of data_pipeline.py scripts design and functionality. For a detailed instruction on how to run the program please run the
following on your command prompt: **python3 data_pipeline.py -help**

## Description
This python script connects with the MensSana_ICU_API and collects data of ICU patients.
The data consists of a unique patient id and medical data such as body temperature, heart rate, etc. for each patient in intensive care unit(s).
After the collection, data is given to a ML model to predict based on medical data wether an alarm should be thrown or not.
The program outputs a text file which contains collected data and corresponding predictions of the model. 

## Usage
The script can be run in two modes: realtime and demo.
These two modes differ in the stopping criterion for data collection.
In the realtime mode, data will be collected until the user presses the ENTER and thus terminates the program. This gives one the flexibility of not having 
to determine the number of data request iterations beforehand. This mode is thought as a draft for future real application of the data pipeline, where
real patients data flow continuously.
