# Process Schedule File Data Visualization Tool

------

## Description

A tool that looks at the `sched` (schedule) file for the top 'n' active processes and visualizes that per process across each of the top 'n' processes.\
Note that this tool can only be used with UNIX based operating systems at the moment (MacOS, Linux)

------

## Usage

Useful for when you want to quickly see the information from the `sched` files of a set number of processes and compare
that information between similar processes at different time intervals on a UNIX based operating system.

------

## Installation and Operation Instructions

1. Clone this project from GitHub into any local directory.
2. Navigate to the directory the script is in within your directory structure and make sure Python is installed on your local system.
3. Run the command `python3 pip install -r requirements.txt` to install the required libraries for this project.
4. Run the command `python3 sched_data_visualization.py [num-pids] [format_option]` using a valid 'num_pids' and 'format_option' field (see main() in `sched_data_visualization.py` for more information on valid inputs.
5. After running the script, use `CTRL + C` to stop the script's operation and either the results of running the script will be within a file called `pid_sched_data.txt` in your working directory.