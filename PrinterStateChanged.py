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

	if (jobInfo['state'] == 'Starting print from SD'): # do not allow to start print from SD card / not yet tested
		logging.info('Job was started from SD card -> cancel job')
		cancel_job()
	#elif (oldState == 'STARTING' and newState == 'CANCELLING'): # cancelled during 'press knob to start'
	elif (newState == 'CANCELLING'): # cancelled, possibly during 'press knob to start'
		logging.info("Job cancelled during 'Press knob to start' -> disconnect")
		# add last idle period before stopping the bridge
		'''
		if (get_pause() != 0):
			# calculate duration of pause and add it to fabman.idleTime
			ts_resume = time.time()
			idleTime = int(get_idleTime()) + int(ts_resume - get_pause())
			put_idleTime(idleTime)
			reset_pause()
		'''
		# stop bridge
		#response = bridge_stop(get_sessionId(), get_idleTime(), get_metadata())
		response = bridge_stop()
		#reset_pause()
		octoprint_disconnect()
	elif (newState == 'OPERATIONAL'): # printer available for new print (job finished, cancelled, etc.)
		try:
			logging.info("Printer available for new print (job finished, cancelled, etc.) -> stop fabman session, if open")
			# add last idle period before stopping the bridge
			if (get_pause() != 0):
				# calculate duration of pause and add it to fabman.idleTime
				ts_resume = time.time()
				idleTime = int(get_idleTime()) + int(ts_resume - get_pause())
				put_idleTime(idleTime)
				reset_pause()
			# stop bridge
			#response = bridge_stop(get_sessionId(), get_idleTime(), get_metadata())
			response = bridge_stop()
			reset_pause()
			#return True
		except Exception as e: 
			logging.error('Function bridge_setBusy raised exception (' + str(e) + ')')
			#return False
	elif (newState == 'STARTING'):
		bridge_start(str(jobInfo['job']['user']))

	# busy/idle detection
	if (newState == 'PRINTING'):
		bridge_setBusy()
	else:
		bridge_setIdle()
	
except Exception as e: 
	logging.error('PrinterStateChanged raised exception (' + str(e) + ')')
	