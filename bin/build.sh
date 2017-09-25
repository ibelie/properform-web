export CLOSURE=$(cd `dirname $0`/../closure; pwd)
export TSPATH=$(cd `dirname $0`/../client; pwd)
export JSPATH=$(cd `dirname $0`/../website/js; pwd)
export GOOGPATH=$(cd `dirname $0`/../website/goog; pwd)
# SET DEBUG=True

tsc --outDir $JSPATH --project $TSPATH

# MD %GOOGPATH%
cp $CLOSURE/lib/closure/goog/base.js $GOOGPATH/
cp $TSPATH/lib/jquery/jquery-3.2.1.min.js $JSPATH/jquery.js

cd $JSPATH
python -B $CLOSURE/lib/closure/bin/build/depswriter.py --root_with_prefix=". ../js" > ../goog/deps.js
