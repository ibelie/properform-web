export BINPATH=$(cd `dirname $0`/bin; pwd)

cd $BINPATH
./build.sh
./run.sh
