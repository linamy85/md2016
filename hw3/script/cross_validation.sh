#!/bin/bash

export SCRIPT=$HOME/md2016/hw3/script

echo "Usage: $0 [directory] [new directory] [time] [command file]"
echo "In command file, one line per command. (NO EMPTY LINES!!!)"

readarray commands < "$4"
echo ${commands[@]}

# Directory processing
if [ -d "$2" ]; then
  echo "Sorry but $2 is already exists, please remove it or change the name."
  exit 1
fi

mkdir $2

cp $1/source.txt $2

ROUND=$3
if [ "$3" == "5fold" ]; then
  ROUND=5
fi

for ((i=1; i<=$ROUND; i++))
do
  echo "Validation #$i"

  # read line and write to $NEW_DIR/test.txt & cross.txt
  if [ "$3" == "5fold" ]; then
    python $SCRIPT/generate_fold.py $1 $2 $(wc $1/train.txt) $i
  else
    python $SCRIPT/generate_valid.py $1 $2
  fi

  cp $2/test.txt $2/test.txt.notused

  RES=""

  for ((c=0; c<${#commands[@]}; c++))
  do
    cp $2/test.txt.notused $2/test.txt

    # execute
    echo "Execute..."
    echo ${commands[c]}
    echo ""

    ${commands[c]}

    TEST_TXT_NUM=$(wc -l < $2/test.txt)
    CROSS_TXT_NUM=$(wc -l < $2/cross.txt)

    if [ "$TEST_TXT_NUM" -ne $CROSS_TXT_NUM ]; then
      echo "Error: test.txt output lines missing..."
      echo "$TEST_TXT_NUM neq $CROSS_TXT_NUM"
      exit 1
    fi

    CURRES=$(python $SCRIPT/scoring.py $2/test.txt $2/cross.txt)
    echo [Round $i:$c] ${commands[c]} :: $CURRES

    RES=$RES" $CURRES"
  done


  # calculate precision
  $SCRIPT/mymf.sh $2/train.txt $2/test.txt $2/mf.out

  MF_RES=$(python $SCRIPT/scoring.py $2/mf.out $2/cross.txt)

  echo "Round $i : $RES / MF: $MF_RES"
  echo "$RES $MF_RES" >> $2/cross.log

done

echo "=========================="
echo "Input: $1"
echo "Output: $2"
echo ""
echo "Total $(( ${#commands[@]} + 1 ))"
python $SCRIPT/simply_count.py $2/cross.log $(( ${#commands[@]} + 1 ))
echo "=========================="

    
#rm -rf NEW_DIR

echo "Done."
