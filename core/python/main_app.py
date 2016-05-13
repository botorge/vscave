"""
+++ main_app.py +++
WHAT'S NEW :
-

THIS MODULE :
-

NOTES :
-
"""

from multiprocessing import Process
from datetime import datetime
from threading import Timer
import os, main_sourcing, main_characterizing, time

def get_secs():
	x = datetime.today()
	y = x.replace(hour=0, minute=1, second=0, microsecond=0)
	delta_t = y-x
	if '-' in str(delta_t):
		try:
			y = y.replace(day=x.day+1)
		except: # to catch a change of month
			y = y.replace(day=1)
			y = y.replace(month=x.month+1)
		delta_t = y-x
	secs = delta_t.seconds+1
	return secs

def reboot(): os.system('echo asdfla|sudo -S reboot')

print "/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"
print "VsCave"
print datetime.now()
# initializing the threads 
p_sourcing = Process(target=main_sourcing.main, args=())
p_characterizing = Process(target=main_characterizing.main, args=())
# start threads
p_sourcing.start()
time.sleep(10)
p_characterizing.start()
# reboot tomorrow
Timer(get_secs(), reboot).start()

