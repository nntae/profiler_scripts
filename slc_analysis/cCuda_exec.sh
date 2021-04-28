#!/bin/bash
EXEC_DIR=$(pwd)
cd /users/scayuela/elastic_cke
echo "Executing cCuda $4 times..."
for ((i=0 ; i<$4; i++)); do
    ./cCuda $1 $2 $3 >>$EXEC_DIR/$2-$3x$4
    echo "Execution #$((i+1)) complete"
done
echo "Done. Output file: $EXEC_DIR/$2-$3x$4"
cd $EXEC_DIR