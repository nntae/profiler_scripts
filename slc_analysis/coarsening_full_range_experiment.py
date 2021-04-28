import subprocess
import sys

if len(sys.argv) < 7:
    sys.exit("Wrong number of arguments")

device = sys.argv[1]
kernel1 = sys.argv[2]
kernel2 = sys.argv[3]
coars1 = sys.argv[4].split(',')
coars2 = sys.argv[5].split(',')
num_exec = sys.argv[6]

for coars_value1 in coars1:
    for coars_value2 in coars2:
        subprocess.call(['./cCuda_full_experiment.sh', device, kernel1, kernel2, coars_value1, coars_value2, num_exec])