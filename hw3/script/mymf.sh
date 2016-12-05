#!/bin/bash

echo "Usage: $0 [train.txt] [test.txt] [out.txt]"

export SCRIPT_DIR=$HOME/md2016/hw3/script

train=/home/yellowfishformd/libmf/mf-train
predict=/home/yellowfishformd/libmf/mf-predict



# -f : L2 norm loss function (def 0)
# -l2 : set l2 regularization parameters (def .1)
# -k : number of dimensions
# -t : iterations
# -p : validation set.

$train -f 0 -l2 0.05 -k 100 -t 100 $1 /tmp/mf.model

echo "Done trainging"

echo "Remove trailing '?' in test file"

python3 $SCRIPT_DIR/testfile_proc.py $2 

$predict -e 0 "$2".proc /tmp/mf.model $3

python3 $SCRIPT_DIR/combine.py "$2".proc $3

rm "$2".proc
