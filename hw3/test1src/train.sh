
export LIBDIR=$HOME/md2016/hw3/test1src

echo "Usage: $0 [dir] [rank] [iteration]"

python2.7 $LIBDIR/test1_cppacc.py $1 $2 $3

echo "Done preprocessing"

g++ -std=c++11 -pthread $LIBDIR/userMatch.cpp -o userMatch
./userMatch $1/tran.txt $1/train.txt $1/match.txt

echo "Done cpp matching"

python2.7 $LIBDIR/postcpp.py $1/match.txt $1/test.txt $2 $3

rm ./userMatch
echo ""
echo "Finally done!"
