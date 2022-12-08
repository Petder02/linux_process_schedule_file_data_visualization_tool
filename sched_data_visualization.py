# System level imports
import os
import sys
from time import sleep

# Data visualization libraries used
import pandas as pd
import numpy as np
from tabulate import tabulate

""" 
Finds all the active processes on the system

Input: 
    N/A
Output: 
    A list containing the PIDs of all processes (non-active and active) on the system
"""
def find_all_pids():
    # Run top, but without the headers. Only want the PID's from the overall output
    processes = os.popen("top -b -n 1 | sed -n '/PID/,$p'|sed '/PID/d'")
    top_output = processes.read()
    processes.close()
    # Write results to text file
    output = "top_results.txt"
    file_out = open(output, 'w')
    file_out.write(top_output)
    file_out.close()
    # PIDs found in top
    pids = []
    # Write pids in file to pids list
    try:
        with open("top_results.txt", 'r') as file_out:
            for line in file_out:
                line = line.strip()
                segments = line.split()
                # If there are no values, return an error cause this should never happen
                if len(segments) <= 0:
                    raise Exception("No data for this PID (should never occur)!")
                elif not segments[0].isnumeric():
                    raise Exception("The first data input should be a PID!")
                else:
                    pids.append(segments[0])
        return pids
    except Exception as e:
        pass

"""
Constructs a dict associating a pid with its sched file
If the pid in question does not have a sched file, it will be skipped

Input:
    pids -> All the pids found in top on this run
Output:
    A dictionary mapping each pid to its sched file (if the sched file exists)
"""
def find_pid_sched_paths(pids):
    # Change working directory to proc
    # os.chdir("/proc")
    sched_paths = dict()
    for pid in pids:
        try:
            sched_path = f"/proc/{pid}/sched"
            # Exclude any processes which do not have sched files
            if not os.path.exists(sched_path):
                raise Exception(f"The sched directory with path -> {sched_path} does not exist!\nIt will be excluded from the final analysis.")
            # PID is guarenteed to be numeric based on input list
            sched_paths[int(pid)] = f"/proc/{pid}/sched";
        except Exception as e:
            pass
    return sched_paths

"""
Constructs a dictionary associating pids with information from their sched file

Input:
    pid_to_sched_file -> A dict mapping each pid to its sched file
Output:
    A dict associating pids with information from their sched file
"""
def construct_pid_sched_file_info_dict(pid_to_sched_file):
    pid_sched_file_info_dict = {}
    line_break_char = '-'
    # Iterate through sched files, get the necessary data
    for pid in pid_to_sched_file.keys():
        first_value_found = False
        sched_file = pid_to_sched_file[pid]
        sched_data = []
        # Run top, but without the headers. Only want the PID's from the overall output
        pid_sched_data = os.popen(f"cp {sched_file} {os.getcwd()}")
        # Read sched file of this pid, get information
        with open(sched_file) as sched_file_out:
            for line in sched_file_out:
                # IF the current line consists of all dashes, the first piece of data is on the next line
                if not first_value_found and line.count(line_break_char) >= len(line) - 1:
                    first_value_found = True
                    continue
                # Once a line with all dashed lines is reached, we have found the start of the info needed
                elif not first_value_found:
                    continue
                # Read all data necessary from sched file
                else:
                    try:
                        line = line.strip()
                        # Remove white space
                        line = line.replace(" ", "")
                        # Category is on the left, data is on the right
                        data = line.split(":")
                        # Two preconditions must hold:
                        if len(data) != 2:
                            raise Exception("Should be only two entries in the data!")
                        if not ((type(data[1]) is float) or (type(data[1] is int))):
                            raise Exception("Second piece of data must be numeric")
                        # Add data to sched data
                        sched_data.append(data[1])
                    except Exception as e:
                        pass
            # Attach data to pid object
        pid_sched_file_info_dict[pid] = sched_data
        print(f"{pid} : {pid_sched_file_info_dict[pid]}\n")
        print(f"number of data points -> {len(pid_sched_file_info_dict[pid])}\n")
    
    return pid_sched_file_info_dict

"""
Constructs the sched data frame based on the given sched info for each pid

Input:
    pid_sched_file_info_dict -> A dictionary mapping each pid to its sched data
    format_option            -> A string specifying which column names to use for the data frame

Output:
    A data frame contatining all information from sched for each pid
    
"""
def construct_sched_data_frame(pid_sched_file_info_dict, format_option):
    # Create data frame with structure depending on input option
    sched_data = {}
    if format_option == "long":
        sched_data = {
            "PID": [],
            "se.exec_start": [],
            "se.vruntime": [],
            "se.sum_exec_runtime": [],
            "se.nr_migrations": [],
            "nr_switches": [],
            "nr_voluntary_switches": [],
            "nr_involuntary_switches": [],
            "se.load.weight": [],
            "se.avg.load_sum": [],
            "se.avg.runnable_sum": [],
            "se.avg.util_sum": [],
            "se.avg.load_avg": [],
            "se.avg.runnable_avg": [],
            "se.avg.util_avg": [],
            "se.avg.last_update_time": [],
            "se.avg.util_est.ewma": [],
            "se.avg.util_est.enqueued": [],
            "policy": [],
            "prio": [],
            "clock-delta": []
        }
    else:
        sched_data = {
            "PID": [],
            "EXEC_ST": [],
            "VRT": [],
            "SERT": [],
            "NR_MIGRs": [],
            "NR_SWs": [],
            "NR_VOL_SWs": [],
            "NR_INVOL_SWs": [],
            "LD_WT": [],
            "LD_SUM": [],
            "RUNNABLE_SUM": [],
            "UTIL_SUM": [],
            "LD_AVG": [],
            "RUNNABLE_AVG": [],
            "UTIL_AVG": [],
            "LAST_UPDT_TIME": [],
            "EWMA": [],
            "ENQUEUED": [],
            "POLICY": [],
            "PRIO": [],
            "CLK_DETLA": []
        }
    # Index dataframe by PID
    sched_data_frame = pd.DataFrame(sched_data)
    # Construct the dataframe row by row
    for pid in pid_sched_file_info_dict:
        sched_file_info = pid_sched_file_info_dict[pid]
        # Make sure to insert pid at front for output
        sched_file_info.insert(0, pid)
        # Add the row to the dataframe
        sched_data_frame.loc[len(sched_data_frame.index)] = sched_file_info
        
    return sched_data_frame

# pids = find_all_pids()
# pid_sched_paths = find_pid_sched_paths(pids)
# pid_sched_file_info_dict = construct_pid_sched_file_info_dict(pid_sched_paths)
# sched_data_frame = construct_sched_data_frame(pid_sched_file_info_dict)
# print(sched_data_frame)
# print(tabulate(sched_data_frame, headers='keys', tablefmt='psql', showindex=False))

# # Make output into a nice table format and write to a file for viewing
# with open("sched_data.txt", 'w') as file:
#     file.write(tabulate(sched_data_frame, headers='keys', tablefmt='psql', showindex=False))

"""
Prints the top n PIDs with their associated sched information in a table format for ease of visualization
    
Inputs taken from the command line arguments:
    num_pids      -> An integer specifying the number of pids to print information for
    format_option -> A string specifying the format which column names should be displayed in. There are two possible formats...
        'short' -> Displays abbreviated sched data names
        'long'  -> Displays full sched data names
Output:
    Using the 'short' format, the output will be generated directly on the command line
    Using the 'long' format, the output will be generated to a text file called 'sched_output.txt'
"""
def main():
    print(sys.argv)
    # Arguments must be of specified types
    num_pids = int(sys.argv[1])
    format_option = str(sys.argv[2])
    # Argument validation
    if num_pids <= 0:
        print("Must display the sched information for at least one process!")
        return
    if not (format_option == "short" or format_option == "long"):
        print("Must supply a format option of either 'short' or 'long'!")
        return
    # Get sched info per pid available
    pids = find_all_pids()
    if num_pids > len(pids):
        print(f"The specified number of pids exceeds the number of pids available.\nThe total number of pids available is {len(pids)}.")
        num_pids = len(pids)
    # Create sched_data given the pids
    pid_sched_paths = find_pid_sched_paths(pids)
    pid_sched_info_dict = construct_pid_sched_file_info_dict(pid_sched_paths)
    sched_data = construct_sched_data_frame(pid_sched_info_dict, format_option)
    # For the short version, also print the results to the console
    # For the long version, because it will be incorrectly formatted in the console, only write it to a file
    # The results of each iteration of the script will be recorded within that file for easy viewing
    if format_option == "short":
        print(f"{tabulate(sched_data.head(num_pids), headers='keys', tablefmt='psql', showindex=False)}\n\n")
    print("Writing results to 'pid_sched_data.txt' in working directory.")
    with open("pid_sched_data.txt", 'a') as file:
        file.write(f"{tabulate(sched_data.head(num_pids), headers='keys', tablefmt='psql', showindex=False)}\n\n")
            
# Runs the program using the main function a set number of times
# You can terminate the program by using CTRL+C, but otherwise it will iterate keep iterating
if __name__ == '__main__':
    # Create new pid_sched_data file
    file = open("pid_sched_data.txt", 'w')
    file.close()
    while (True):
        main()
        # Delete files created by functions
        
        sleep(2.0)
