
export LIBDIR=$HOME/md2016/hw3/test1src

python2.7 $LIBDIR/test1_cppacc.py $1

echo "Done preprocessing"

g++ -std=c++11 -pthread $LIBDIR/userMatch.cpp -o userMatch
./userMatch $1/tran.txt $1/train.txt $1/match.txt

echo "Done cpp matching"

python2.7 $LIBDIR/postcpp.py $1/match.txt $1/test.txt

rm ./userMatch
echo ""
echo "Finally done!"
