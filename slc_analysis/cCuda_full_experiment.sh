#!/bin/bash
# Makes cCuda and runs a profiling experiment, first running nvprof and then executing cCuda several times to get statistics about the speedup results.
EXEC_DIR=$(pwd)
DEVICE=$1
KERNEL1=$2
KERNEL2=$3
COARS1=$4
COARS2=$5
NUM_EXEC=$6
CCUDA_DIR=$7
BASE_FILENAME=${KERNEL1}x${COARS1}-${KERNEL2}x${COARS2}
EXEC_FILENAME="exec_$BASE_FILENAME"
TRACE_FILENAME="trace_$BASE_FILENAME"
CSV_FILENAME="$KERNEL1-$KERNEL2.csv"
DIRNAME="$KERNEL1-$KERNEL2"

if (( $# < 6 )); then
    echo "Usage: $0 <DEVICE-ID> <KERNEL1> <KERNEL2> <COARS1> <COARS2> <NUM_EXEC>"
    exit
fi

echo "Running full experiment on $DEVICE of $KERNEL1 with coarsening factor $COARS1 and $KERNEL2 with coarsening factor $COARS2. Executing $NUM_EXEC times to get speedup average"
echo $7

if [[ -z "$CCUDA_DIR" ]]; then
    cd /users/scayuela/elastic_cke
else
    cd $CCUDA_DIR
fi
echo "Running make..."
make cCuda

echo "Running nvprof..."
nvprof --normalized-time-unit ns --print-gpu-trace --csv --log-file $EXEC_DIR/$TRACE_FILENAME ./cCuda $DEVICE $KERNEL1 $KERNEL2 $COARS1 $COARS2
echo "Done. Output file: $EXEC_DIR/$TRACE_FILENAME"

echo "Executing cCuda $NUM_EXEC times..."
for ((i=0 ; i<$NUM_EXEC; i++)); do
    ./cCuda $DEVICE $KERNEL1 $KERNEL2 $COARS1 $COARS2 >>$EXEC_DIR/$EXEC_FILENAME
    echo "Execution #$((i+1)) complete"
done
cd $EXEC_DIR
echo "Done. Output file: $EXEC_DIR/$EXEC_FILENAME"

echo "Running slc_analysis.py..."
python3 slc_analysis.py $TRACE_FILENAME $COARS1 $COARS2 $EXEC_FILENAME $CSV_FILENAME

if [ ! -d "$DIRNAME" ]; then
    echo "Making directory: $DIRNAME"
    mkdir $DIRNAME
fi
    echo "Moving temp files to $DIRNAME"
    mv exec_$KERNEL1*-$KERNEL2* $DIRNAME/
    mv trace_$KERNEL1*-$KERNEL2* $DIRNAME/