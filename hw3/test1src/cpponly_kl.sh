#!/bin/bash

MATRIX_DIR=/tmp3/b03902055
SRC_DIR=$HOME/md2016/hw3/test1src
LIBNMF=$HOME/version_1.02
LIBFM=$HOME/libfm-1.42.src

# ----------------------------------
# LibFM format:
# user index -> user index
# item index -> 50000 + item index
# ----------------------------------

# Monitor mode.  Job control is enabled.
set -m  

if [ "$1" == "-h" ]; then
  echo "Usage: $0 [dir] [valid(y/n)] [1st iter] [session] [dim '1,1,30'] [2nd iter]"
  #                 $1      $2           $3        $4         $5           $6
  echo "Example: $0 test1 test1_new y 100 3 '1,1,40' 20"
  exit 0
fi

echo "Hello, this is Cpp only version of test1."
echo "The matrix file is store in $MATRIX_DIR directory."
echo "Usage: $0 [directory] [valid? (y/n)] [iter] [session id] [dim] [test iter]"
echo "If valid = y then train.matrix.* will be replaced."

# Check directory exists.
if [ ! -d $1 ]; then
  echo ""
  echo "Error! $1 does not exists..."
  exit 1
fi

echo ""

session=$4
if [ "$4" == "" ]; then
  session=0
fi
echo "Session Id: $session"
echo ""
# ------------------------------------------------------------------------------

#### Step 0: Transfer to Libfm format.
# * source.txt => source.libfm
# * train.txt => train.libfm
echo "--------------------- Step 0 : Transfer [$(date)] ------------------------"

if [ ! -f $MATRIX_DIR/source.libfm.0 ]; then
  echo "source matrix 0 doesn't exist, creating it..."
  python $SRC_DIR/tolibfm.py $1/source.txt $MATRIX_DIR/source.libfm.0 y
fi

if [ "$2" == "y" ] || [ ! -f $MATRIX_DIR/train.libfm.$session ]; then
  echo "train matrix 0 doesn't exist, creating it..."
  python $SRC_DIR/tolibfm.py $1/train.txt $MATRIX_DIR/train.libfm.$session y
fi

# Make the libfm format for full matrix: user x item
if [ ! -f $MATRIX_DIR/full.libfm ]; then
  echo "Full matrix 0 doesn't exist, creating it..."
  python $SRC_DIR/step0.py $MATRIX_DIR/full.libfm
fi

# ------------------------------------------------------------------------------

#### Step 1: Extend matrix
# * Matrix Factorization for source & target
# * This step only need to be done once!
#   (So we can thus choosing the one producing the best result.)

echo "--------------------- Step 1 : LibFM [$(date)] ------------------------"

#gcc -Wall $SRC_DIR/step1.c -I$LIBNMF/include -L$LIBNMF/lib -lnnmf -larpack -llapack -lblas -lm -o step1

if [ ! -f $MATRIX_DIR/source.matrix.1 ]; then
  echo "source matrix 1 doesn't exist, running FM..."
  $LIBFM/bin/libFM -task r -train $MATRIX_DIR/source.libfm.0 \
    -test $MATRIX_DIR/full.libfm -dim $5 -out $MATRIX_DIR/source.matrix.1 \
    -iter $3 &
fi

if [ "$2" == "y" ] || [ ! -f $MATRIX_DIR/train.matrix.$session ]; then
  echo "train matrix 1 doesn't exist, running MF..."
  $LIBFM/bin/libFM -task r -train $MATRIX_DIR/train.libfm.$session \
    -test $MATRIX_DIR/full.libfm -dim $5 -out $MATRIX_DIR/train.matrix.$session \
    -iter $3 &
  sleep 3
fi

fg
fg
echo "LibFM done job."

# ------------------------------------------------------------------------------

#### Step 2: Find item matching
# * Reduce source & target matrix to item distribution
# * Compute pairwise cost
# * Hungarian: find the best matching in O(n^3)

#### Step 3: Find user matching
# * Read in extended source matrix, do rearrange.
# * For each user in target domain,
#     fill in its data with the user in source domain with max dot similarity.
# * Output the resulting matrix [in libfm format].

echo "--------------------- Step 2 & 3 [$(date)] ------------------------"

# Compiles object file in current directory.
g++ -Wall -O3 -std=c++11 -pthread $SRC_DIR/step23_kl.cpp -o step23_kl

./step23_kl $MATRIX_DIR/source.matrix.1 $1/source.txt \
  $MATRIX_DIR/train.matrix.$session $1/train.txt $MATRIX_DIR/mytrain.libfm.$session

rm step23 step23.o bipartite-mincost.o 

# ------------------------------------------------------------------------------

#### Step 4: Extend information & output
# * Matrix factorization
# * Fill out the result to test.txt

echo "--------------------- Step 4 [$(date)] ------------------------"

python $SRC_DIR/tolibfm.py $1/test.txt $MATRIX_DIR/test.libfm.$session n

$LIBFM/bin/libFM -task r -train $MATRIX_DIR/mytrain.libfm.$session \
  -test $MATRIX_DIR/test.libfm.$session -dim $5 -out $1/test.out \
  -iter $6

python $SRC_DIR/combine.py $1/test.txt $1/test.out

# ------------------------------------------------------------------------------

echo "Done output result of test1."
