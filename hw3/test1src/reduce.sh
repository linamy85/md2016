SCRIPT=$HOME/md2016/hw3/script
MATRIX_DIR=/tmp3/b03902055
SRC_DIR=$HOME/md2016/hw3/test1src
LIBFM=$HOME/libfm-1.42.src

cp $1/test.txt.notused $1/test.txt
python $SRC_DIR/tolibfm.py $1/test.txt $MATRIX_DIR/test.libfm.long n
for i in 70 100 
do
  cp $1/test.txt.notused $1/test.txt

  $LIBFM/bin/libFM -task r -train $MATRIX_DIR/mytrain.libfm.long \
    -test $MATRIX_DIR/test.libfm.long -dim '1,1,30' -out $1/test.out \
    -iter $i

  python $SRC_DIR/combine.py $1/test.txt $1/test.out

  ANS=$(python $SCRIPT/scoring.py $1/test.txt $1/cross.txt)
  echo "$i: $ANS"
  echo $ANS >> $1/cross.log
done


#cp $1/test.txt.notused $1/test.txt
#$SCRIPT/mymf.sh $1/train.txt $1/test.txt $1/mf.out

#echo "libfm: "
#python $SCRIPT/scoring.py $1/mf.out $1/cross.txt
