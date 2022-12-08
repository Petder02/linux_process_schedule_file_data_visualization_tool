import os
import pandas as pd
import numpy as np

""" 
Finds all the active processes on the system

Input: 
    N/A
Output: 
    A list containing the PIDs of all processes (non-active and active) on the system
"""
def find_all_pids() -> list[str]:
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
def find_pid_sched_paths(pids: list[str]) -> dict[int, str]:
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
def construct_pid_sched_file_info_dict(pid_to_sched_file: dict[int, str]) -> dict[int, list[str]]:
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
Constructs data frame containing information found in sched

Input:
    pid_sched_file_info_dict -> A dict containing sched info per process
Output:
    A data frame containing sched information organized by process, across all processes
"""
def construct_sched_data_frame(pid_sched_file_info_dict: dict[str]):
    # Create data frame with structure
    sched_data = {
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
    sched_data_frame = pd.DataFrame(sched_data)
    
    
    
pids = find_all_pids()
pid_sched_paths = find_pid_sched_paths(pids)
pid_sched_file_info_dict = construct_pid_sched_file_info_dict(pid_sched_paths)
construct_sched_data_frame(pid_sched_file_info_dict)
