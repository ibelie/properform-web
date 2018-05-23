export PYTHONPATH=$(cd `dirname $0`/../server; pwd)
export APP_ROUTE=$PYTHONPATH/handler
export FILE_PATH=$(cd `dirname $0`/../website; pwd)

nohup python -B $PYTHONPATH/tarantula.py -a $APP_ROUTE -f $FILE_PATH -p 15555 -l properform > log.txt &
