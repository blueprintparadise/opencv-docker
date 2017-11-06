matar=`ps axu | grep python\ servidor-cv.py | grep -v grep | awk '{print $2}'`
kill -9 $matar

matar=`ps axu | grep python\ cliente-cv.py | grep -v grep | awk '{print $2}'`
kill -9 $matar