exec(open("/home/pi/fabman/fabmanFunctions.py").read())

'''
OPEN_SERIAL
DETECT_SERIAL
DETECT_BAUDRATE
CONNECTING
OPERATIONAL
PRINTING
PAUSED
CLOSED
ERROR
CLOSED_WITH_ERROR
TRANSFERING_FILE
OFFLINE
UNKNOWN
NONE

STARTING
FINISHING
'''

try:
	newState = sys.argv[1]
	oldState = get_printerState()
	put_printerState(newState)
	jobInfo = get_job_info()

	logging.info("Printer state changed from " + oldState +  " to " + newState + ' (user: ' + str(jobInfo['job']['user']) + ' / state: ' + str(jobInfo['state']) + ')')

	if (newState == 'STARTING'):
		bridge_start(str(jobInfo['job']['user']))
	elif (jobInfo['state'] == 'Starting print from SD'): # do not allow to start print from SD card / not yet tested
		logging.info('Job was started from SD card -> cancel job')
		cancel_job()
	elif (newState == 'CANCELLING'): # cancelled, possibly during 'press knob to start'
		logging.info("Job cancelled during 'Press knob to start' -> disconnect")
		bridge_stop()
		octoprint_disconnect()
	elif (newState == 'OPERATIONAL'): # printer available for new print (job finished, cancelled, etc.)
		logging.info("Printer available for new print (job finished, cancelled, etc.) -> stop fabman session, if open")
		bridge_stop()

except Exception as e: 
	logging.error('PrinterStateChanged raised exception (' + str(e) + ')')
	