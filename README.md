# Flight-within-USA-Displayer
A program to compute and show delay information about US flights based on data from January 2020 (around 500k flights). The information includes departure delay, arrival delay, percentage of diverted flights, and percentage of canceled flights.

## How to run
### Start a virtual environment (optional)
1\) Create a virtual environment
```
python -m venv env
```
2\) Activate the virtual environment</br>
```
# Activate the virtual env on Linux and MacOS
source env/bin/activate
# Or, on MS Windows:
env\Scripts\activate
```
### Install all the packages required by the program
```
pip install -r requirements.txt
```
### Start the program
The program need a few seconds before displaying UI
```
python main.py
```
### Stop the program
Click the exit tab in the UI, then exit the virtualenv using:
```
deactivate
```
## Project Documents
All project-related documents are in the [Project Wiki](https://github.com/BioB3/Flight-within-USA-Displayer/wiki)