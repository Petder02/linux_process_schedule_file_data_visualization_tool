import os

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
        print(e)

"""
Gets all the sched map paths for the pids found in top

Input:
    pids -> All the pids found in top on this run
Output:
    A list with all the sched paths for the pids found after reading from top
"""
def find_pid_sched_paths(pids: list[str]) -> list[str]:
    # Change working directory to proc
    os.chdir("/proc")
    sched_paths = []
    for pid in pids:
        try:
            sched_path = f"/proc/{pid}/sched"
            # Exclude any processes which do not have sched files
            if not os.path.exists(sched_path):
                raise Exception(f"The sched directory with path -> {sched_path} does not exist!\nIt will be excluded from the final analysis.")
            sched_paths.append(f"/proc/{pid}/sched")
        except Exception as e:
            print(e)
    return sched_paths
