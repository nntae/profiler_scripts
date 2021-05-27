#!/bin/bash
gpu=$1
python3 coarsening_full_range_experiment.py ${gpu} GCEDD Reduction 1,2,3 1,2,4,8,16,32,64,128 3 &&
python3 coarsening_full_range_experiment.py ${gpu} MM Reduction 1 1,2,4,8,16,32,64 3 &&
python3 coarsening_full_range_experiment.py ${gpu} PF Reduction 1 1,2,4,8,16,32,64,128 3 &&
python3 coarsening_full_range_experiment.py ${gpu} GCEDD BS 1,2,3 1,2,4,8,16,32,64,128 3 &&
python3 coarsening_full_range_experiment.py ${gpu} MM BS 1 1,2,4,8,16,32,64 3 &&
python3 coarsening_full_range_experiment.py ${gpu} PF BS 1 1,2,4,8,16,32,64 3 &&
python3 coarsening_full_range_experiment.py ${gpu} GCEDD VA 1,2,3 1,2,4,8,16,32,64 3 &&
python3 coarsening_full_range_experiment.py ${gpu} MM VA 1 1,2,4,8,16,32 3 &&
python3 coarsening_full_range_experiment.py ${gpu} PF VA 1 1,2,4,8,16,32,64 3