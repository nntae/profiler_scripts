import csv
import sys
from statistics import mean, stdev
import re
import os

"""Parse the csv output of nvprof"""
def parse_gpu_trace_csv(filename):
    with open(filename, newline='') as log:
        kernels = dict()
        line = "=" # Logger's lines start with "="
        # Skip logger's messages
        while line[0] == "=":
            pos = log.tell()
            line = log.readline()

        log.seek(pos)
        timeline = csv.DictReader(log)

        for execution in timeline:
            match = re.match("[^\(\[]+", execution["Name"])
            if match != None:
                kernel_name = match[0]
                execution["Name"] = kernel_name
                kernels.setdefault(kernel_name,[]).append(execution)

    return kernels

"""Parse an array of dicts representing the GPU trace of the executions of one kernel"""
def parse_kernel_trace(trace):
    executions = []

    first = trace[0]
    kernel_name = first["Name"]
    prev_grid_size = int(float(first["Grid X"]))
    start_times = [int(float(first["Start"]))]
    durations = [int(float(first["Duration"]))]

    for execution in trace[1:]:
        grid_size = int(float(execution["Grid X"]))
        start = int(float(execution["Start"]))
        duration = int(float(execution["Duration"]))
        grid_size_ratio = grid_size/prev_grid_size if grid_size > prev_grid_size else prev_grid_size/grid_size

        if (grid_size_ratio < 1): # error
            print("Grid size error: " + str(grid_size) + " (prev_grid_size = " + str(prev_grid_size) + ")")
            sys.exit(1)
        elif (grid_size_ratio == 1): # same grid config
            start_times.append(start)
            durations.append(duration)
        elif (grid_size_ratio > 3 and start_times): # reached the end of the sliced execution (it executes a larger, single slice with a grid size equal to the sum of grid sizes of the slices that have been executed in the coexecution time. it is detected here)
            executions.append({'durations': durations, 'start_times': start_times, 'grid_size': prev_grid_size})
            start_times = []
            durations = []
        else: # new grid config
            start_times.append(start)
            durations.append(duration)
            prev_grid_size = grid_size

    kernel = {'name': kernel_name, 'executions': executions}

    return kernel

"""Parse an individual csv representing the GPU trace of one kernel"""
def parse_csv(filename):
    start_times = []
    durations = []
    executions = []

    with open(filename) as csvfile:
        timeline = csv.DictReader(csvfile)
        first = next(timeline)
        prev_grid_size = int(first["Grid X"])
        kernel_name = re.match("[^\[\(]+", first["Name"])[0]

        for execution in timeline:
            grid_size = int(execution["Grid X"])
            grid_size_ratio = grid_size/prev_grid_size if grid_size > prev_grid_size else prev_grid_size/grid_size

            if (grid_size_ratio < 1):
                print("Grid size error: " + str(grid_size) + " (prev_grid_size = " + str(prev_grid_size) + ")")
                sys.exit(1)
            elif (grid_size_ratio == 1):
                start_times.append(int(execution["Start Time(ns)"]))
                durations.append(int(execution["Duration(ns)"]))
            elif (grid_size_ratio > 3 and start_times):
                executions.append({'durations': durations, 'start_times': start_times, 'grid_size': prev_grid_size})
                start_times = []
                durations = []
            else:
                start_times.append(int(execution["Start Time(ns)"]))
                durations.append(int(execution["Duration(ns)"]))
                prev_grid_size = grid_size

    kernel = {'name': kernel_name, 'executions': executions}

    return kernel

def parse_execution_output(filename):
    speedups = dict()
    speedup_stats = []

    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        
        for line in reader:
            partition = line[1]
            speedup = line[2]
            speedups.setdefault(partition,[]).append(float(speedup))
    
    for speedup_data in speedups.values():
        stats_dict = dict()
        stats_dict["speedup_mean"] = mean(speedup_data)
        stats_dict["speedup_stdev"] = stdev(speedup_data) if len(speedup_data) > 1 else 0
        speedup_stats.append(stats_dict)
    
    return speedup_stats

def set_times_shortest_kernel(exec_):
    idle_times = []
    prev_end_time = exec_["start_times"][0] + exec_["durations"][0]

    for start_time, duration in zip(exec_["start_times"][1:], exec_["durations"][1:]):
        idle_times.append(start_time - prev_end_time)
        prev_end_time = start_time + duration
    
    exec_["idle_times"] = idle_times

def set_times_longest_kernel(exec_, slicing_end_time):
    idle_times = []
    prev_end_time = exec_["start_times"][0] + exec_["durations"][0]
    i = 1

    while exec_["start_times"][i] < slicing_end_time:
        idle_times.append(exec_["start_times"][i] - prev_end_time)
        prev_end_time = exec_["start_times"][i] + exec_["durations"][i]
        i += 1
    
    exec_["idle_times"] = idle_times
    exec_["start_times"] = exec_["start_times"][0:i]
    exec_["durations"] = exec_["durations"][0:i]

def append_idle_times(exec1, exec2):
    if exec1["start_times"][-1]+exec1["durations"][-1] >= exec2["start_times"][-1]+exec2["durations"][-1]:
        longest = exec1
        shortest = exec2
    else:
        longest = exec2
        shortest = exec1
    
    slicing_end_time = shortest["start_times"][-1] + shortest["durations"][-1]
    set_times_longest_kernel(longest, slicing_end_time)
    set_times_shortest_kernel(shortest)

def append_all_idle_times(execs1, execs2):
    for exec1, exec2 in zip(execs1, execs2):
        append_idle_times(exec1, exec2)

def get_stats(execution):
    try:
        idle_times = execution["idle_times"]
        total_idle_time = sum(idle_times)

        if (len(idle_times)) > 0:
            average_idle_time = int(round(mean(idle_times)))
            stdev_idle_time = int(round(stdev(idle_times,average_idle_time)))
        else:
            average_idle_time = 0
            stdev_idle_time = 0

        wall_time = execution["start_times"][-1] + execution["durations"][-1] - execution["start_times"][0]
        average_execution_time = int(round(mean(execution["durations"]),0))
        stdev_execution_time = int(round(stdev(execution["durations"],average_execution_time))) if len(execution["durations"]) > 1 else 0
        percent_of_total = round(total_idle_time / wall_time * 100, 4)
        return {'wall_time': wall_time, 'average_execution_time': average_execution_time, 'stdev_execution_time': stdev_execution_time, 'total_idle_time': total_idle_time, 'average_idle_time': average_idle_time, 'stdev_idle_time': stdev_idle_time, 'percent_of_total': percent_of_total}
    except KeyError as exc:
        raise RuntimeError('Error getting stats') from exc

def print_idle_times(kernel):
    print("-----------------------------")
    print("Kernel: " + kernel["name"])
    print("-----------------------------")
    print("# of executions: " + str(len(kernel["executions"])))
    for i in range(len(kernel["executions"])):
        execution = kernel["executions"][i]
        stats = get_stats(execution)
        print("\nExecution " + str(i+1) + "(Grid size: " + str(execution["grid_size"]) + ")")
        print("-----------")
        print("Idle times: " + str(execution["idle_times"]) + "\n")
        print("Elapsed time: " + str(stats["wall_time"]) + " ns")
        print("Total idle time: " + str(stats["total_idle_time"]) + " ns")
        print("Std. deviation of idle time: " + str(stats["stdev_idle_time"]) + " ns")
        print("Average idle time: " + str(stats["average_idle_time"]) + " ns")
        print("Average execution time: " + str(stats["average_execution_time"]) + " ns")
        print("Std. deviation of execution time: " + str(stats["stdev_execution_time"]) + " ns")
        print("% of total: " + str(stats["percent_of_total"]))
    print('')

def print_to_csv(kernel1, kernel2, coarsening1, coarsening2, speedup_stats=None, filename=''):
    if (filename == ''):
        filename = kernel1["name"] + '-' + kernel2["name"] + ".csv"
    kernel_fieldnames1 = ['elapsed_time1', 'average_execution_time1', 'stdev_exec_time1', 'total_idle_time1', 'average_idle_time1', 'stdev_idle_time_1', 'percent_of_total1']
    kernel_fieldnames2 = ['elapsed_time2', 'average_execution_time2', 'stdev_exec_time2', 'total_idle_time2', 'average_idle_time2', 'stdev_idle_time_2', 'percent_of_total2']
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['execution', 'grid_size1', 'grid_size2', 'coarsening1', 'coarsening2'] + kernel_fieldnames1 + kernel_fieldnames2 + ['speedup_mean', 'speedup_stdev']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if (not os.path.exists(filename) or os.stat(filename).st_size == 0):
            writer.writeheader()

        for i in range(len(kernel1["executions"])): 
            try:
                stats1 = get_stats(kernel1["executions"][i])
                stats2 = get_stats(kernel2["executions"][i])
                stats1 = dict(zip(kernel_fieldnames1,stats1.values()))
                stats2 = dict(zip(kernel_fieldnames2,stats2.values()))
                row = {'execution': str(i+1), 'grid_size1': kernel1["executions"][i]["grid_size"], 'grid_size2': kernel2["executions"][i]["grid_size"], 'coarsening1': coarsening1, 'coarsening2': coarsening2, **stats1, **stats2}

                if (speedup_stats != None):
                    row = {**row, **speedup_stats[i]}

                writer.writerow(row)
            except RuntimeError:
                print("Error getting statistics. Possibly only one of the kernels was executed. Skipping execution.")
    print("Output successfully to " + filename)

print("Starting slicing analysis script...")
# Read CSV from command line
if (len(sys.argv) < 4):
    print("Usage: python3 slc_analysis.py <csv-filepath> <coarsening-factor1> <coarsening-factor2> [speedup-csv]")
    sys.exit("Wrong number of arguments")

split_trace = parse_gpu_trace_csv(sys.argv[1])
coarsening1 = sys.argv[2]
coarsening2 = sys.argv[3]
kernels = []

for trace in split_trace.values():
    kernels.append(parse_kernel_trace(trace))

append_all_idle_times(kernels[0]["executions"],kernels[1]["executions"])

if (len(sys.argv) > 4):
    speedup_csv = sys.argv[4]
    speedup_stats = parse_execution_output(speedup_csv)
else:
    speedup_stats = None

if (len(sys.argv) > 5):
    filename = sys.argv[5]
    print("slc_analysis: I've read the speedup csv from " + sys.argv[5])
else:
    filename = ''

print("slc_analysis: I've read the trace csv from " + sys.argv[1])

#print_idle_times(kernels[1])
print_to_csv(kernels[0],kernels[1],coarsening1,coarsening2,speedup_stats,filename)