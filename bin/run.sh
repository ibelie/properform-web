export PYTHONPATH=$(cd `dirname $0`/../server; pwd)
export APP_ROUTE=$PYTHONPATH/handler
export FILE_PATH=$(cd `dirname $0`/../website; pwd)

python -B $PYTHONPATH/tarantula.py $APP_ROUTE $FILE_PATH 80 traceback
