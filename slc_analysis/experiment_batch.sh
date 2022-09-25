#!/bin/bash
gpu=$1
ccuda_dir=$2
 python3 coarsening_full_range_experiment.py ${gpu} GCEDD Reduction 1,2,4,8,16,32 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
 python3 coarsening_full_range_experiment.py ${gpu} MM Reduction 1 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} PF Reduction 1 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} GCEDD BS 1,2,4,8,16,32 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} MM BS 1 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
# python3 coarsening_full_range_experiment.py ${gpu} PF BS 1 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} GCEDD VA 1,2,4,8,16,32 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} MM VA 1 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} PF VA 1 1,2,4,8,16,32,64,128 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} PF RCONV 1 1,2,4,8,16,24 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} MM RCONV 1 1,2,4,8,16,24 7 ${ccuda_dir} &&
python3 coarsening_full_range_experiment.py ${gpu} GCEDD RCONV 1,2,4,8,16 1,2,4,8,16,24 7 ${ccuda_dir} &&
echo "Finished"