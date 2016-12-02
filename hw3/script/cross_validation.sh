#!/bin/bash


echo "Usage: $0 [directory] [new directory] [time] [execution......]"

echo "Please make sure you're now in root of hw3 directory."


# Directory processing
if [ -d "$2" ]; then
  echo "Sorry but $2 is already exists, please remove it or change the name."
  exit 1
fi

mkdir $2

cp $1/source.txt $2

for ((i=1; i<=$3; i++))
do
  echo "Validation #$i"

  # read line and write to $NEW_DIR/test.txt & cross.txt
  python generate_valid.py $1 $2

  # execute
  echo "Execute..."
  echo ${@:4}
  echo ""

  ${@:4}

  TEST_TXT_NUM=$(wc -l < $2/test.txt)
  CROSS_TXT_NUM=$(wc -l < $2/cross.txt)

  if [ "$TEST_TXT_NUM" -ne $CROSS_TXT_NUM ]; then
    echo "Error: test.txt output lines missing..."
    echo "$TEST_TXT_NUM neq $CROSS_TXT_NUM"
    exit 1
  fi

  # calculate precision
  RES=$(python scoring.py $2/test.txt $2/cross.txt)

  echo $RES >> $2/cross.log
  echo "Round $i : $RES"

done

echo "=========================="
echo "Input: $1"
echo "Output: $2"
echo ""
python simply_count.py $2/cross.log
echo "=========================="

    
#rm -rf NEW_DIR

echo "Done."
