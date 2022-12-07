import os

""" 
Finds all the active processes on the system

Input: N/A
Output: A list containing the PIDs of all processes (non-active and active) on the system
"""
def find_all_pids() -> list:
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
                print(line)
                print(segments)
                # If there are no values, return an error cause this should never happen
                if len(segments) <= 0:
                    raise ValueError("No data for this PID (should never occur)!")
                elif not segments[0].isnumeric():
                    raise ValueError("The first data input should be a PID!")
                else:
                    pids.append(segments[0])
        return pids
    except ValueError:
        print ("Something went wrong with reading from top_results!")
    
print(find_all_pids())
