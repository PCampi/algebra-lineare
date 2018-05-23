"""Memory profiler for processes."""

import calendar
import csv
import pathlib
import platform
import sys
import time

import psutil

if __name__ == '__main__':
    """Main function."""
    if len(sys.argv) in {1, 2, 3}:
        raise ValueError(
            "Should call with the process PID, the sampling interval and the outfile name"
            +
            "Example call is: 'python mem_profiler.py 4422 0.1 matlab_memory_log.csv"
        )

    csv_fields = ['timestamp', 'memory_physical(kB)', 'memory_virtual(kB)']

    pid = int(sys.argv[1])  # the sampled process PID
    sampling_interval = float(sys.argv[2])  # the sampling interval
    filepath = sys.argv[3]

    system = 'ubuntu' if platform.system == 'Linux' else 'windows'
    filepath = system + "-" + filepath

    if not '.csv' in filepath:
        filepath = filepath + '.csv'

    if not psutil.pid_exists(pid):
        raise ValueError("Wrong pid {} doesn't exist".format(pid))

    myfile = pathlib.Path(filepath)
    if not myfile.is_file():
        with open(filepath, 'w') as outfile:
            outfile.write(",".join(csv_fields) + "\n")

    process = psutil.Process(pid=pid)
    system = 'Ubuntu' if platform.system() == 'Linux' else 'Windows'
    kilobyte = 1024

    rows = []
    num_rows = 0
    max_row_buffer = 1000
    outfile = open(filepath, 'a')
    csv_writer = csv.DictWriter(outfile, delimiter=',', fieldnames=csv_fields)

    try:
        sample = 0
        print("Sampling process with pid: {}".format(pid))

        while True:
            memory = process.memory_info()
            physical_memory = memory.rss / kilobyte
            virtual_memory = memory.vms / kilobyte
            now = time.time()
            row = {
                'timestamp': now,
                'memory_physical(kB)': physical_memory,
                'memory_virtual(kB)': virtual_memory
            }
            rows.append(row)

            num_rows = num_rows + 1
            if num_rows == max_row_buffer:
                csv_writer.writerows(rows)
                rows = []
                num_rows = 0

            sample = sample + 1
            if sample == 20:
                print("Memory: virtual {:4.2f} MB, resident {:4.2f} MB".format(
                    virtual_memory / 1024, physical_memory / 1024))
                sample = 0

            time.sleep(sampling_interval)

    except (ProcessLookupError, psutil._exceptions.NoSuchProcess,
            psutil._exceptions.AccessDenied, KeyboardInterrupt):
        if rows:
            csv_writer.writerows(rows)

        outfile.close()
        if outfile.closed:
            print("Memory log file closed.")

        print("\nFinished sampling process with pid {}. Results are in {}".
              format(pid, filepath))
