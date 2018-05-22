"""Memory profiler for processes."""

import calendar
import csv
import datetime
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

    csv_fields = ['timestamp', 'memory_physical(MB)', 'memory_virtual(MB)']

    pid = int(sys.argv[1])  # the sampled process PID
    sampling_interval = float(sys.argv[2])  # the sampling interval
    filepath = sys.argv[3]

    if not psutil.pid_exists(pid):
        raise ValueError("Wrong pid {} doesn't exist".format(pid))

    myfile = pathlib.Path(filepath)
    if not myfile.is_file():
        with open(filepath, 'w') as outfile:
            outfile.write(",".join(csv_fields) + "\n")

    process = psutil.Process(pid=pid)
    system = 'Ubuntu' if platform.system() == 'Linux' else 'Windows'
    megabyte = 1024 * 1024

    try:
        with open(filepath, 'a') as outfile:
            csv_writer = csv.DictWriter(
                outfile, delimiter=',', fieldnames=csv_fields)
            print("Sampling process with pid: {}".format(pid))

            sample = 0
            while True:
                memory = process.memory_info()
                physical_memory = memory.rss / megabyte
                virtual_memory = memory.vms / megabyte
                now = datetime.datetime.utcnow().utctimetuple()
                unix_time = calendar.timegm(now)
                row = {
                    'timestamp': unix_time,
                    'memory_physical(MB)': physical_memory,
                    'memory_virtual(MB)': virtual_memory
                }
                csv_writer.writerow(row)
                sample = sample + 1
                if sample == 20:
                    print(
                        "Memory: virtual {:4.2f}MB, resident {:4.2f}MB".format(
                            virtual_memory, physical_memory))
                    sample = 0
                time.sleep(sampling_interval)

    except KeyboardInterrupt:
        print("\nSampling finished. Results are in {}".format(filepath[2:]))
