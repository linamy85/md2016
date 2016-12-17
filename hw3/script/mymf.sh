#!/bin/bash

echo "Usage: $0 [train.txt] [test.txt] [out.txt]"

ITER=100
if [ "$4" != "" ]; then
  ITER=$4
fi

export SCRIPT_DIR=$HOME/md2016/hw3/script

MATRIX_DIR=$HOME/steady
SRC_DIR=$HOME/md2016/hw3/test1src
LIBFM=$HOME/libfm-1.42.src

python $SRC_DIR/tolibfm.py $1 train_ori.libfm y
python $SRC_DIR/tolibfm.py $2 test_ori.libfm n

$LIBFM/bin/libFM -task r -train train_ori.libfm \
  -test test_ori.libfm -out $3 -iter $ITER 

rm train_ori.libfm
rm test_ori.libfm

python $SCRIPT_DIR/combine.py $2 $3 
# -f : L2 norm loss function (def 0)
# -l2 : set l2 regularization parameters (def .1)
# -k : number of dimensions
# -t : iterations
# -p : validation set.

#$train -f 0 -l2 0.05 -k 100 -t 100 $1 /tmp/mf.model

#echo "Done trainging"

#echo "Remove trailing '?' in test file"

#python3 $SCRIPT_DIR/testfile_proc.py $2 

#$predict -e 0 "$2".proc /tmp/mf.model $3

#python3 $SCRIPT_DIR/combine.py "$2".proc $3

#rm "$2".proc
