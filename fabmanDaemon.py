exec(open("/home/pi/fabman/fabmanFunctions.py").read())

# avoid daemon to be started twice
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

try:
	logging.info("Starting daemon")
	delay = 30
	
except Exception as e: 
	logging.error('Initialization of Daemon raised exception (' + str(e) + ')')
	
try:
	metadata = get_metadata()
	progressOld = float(metadata["progress"]["completion"])
except:
	progressOld = 0.0

try:
	bridge_stop()
except Exception as e: 
	logging.error('Daemon raised exception during initialization (' + str(e) + ')')
	
while 1:
	try:
		metadata = get_metadata()
		progress = float(metadata["progress"]["completion"])
	except:
		logging.debug('No progress data available: set progress to 0')
		progress = 0.0

	try:
		logging.info("Heartbeat")
		bridgeData = bridge_heartbeat() 

		# try to reconnect if printer is offline
		if (printer_isOffline(metadata)):
			octoprint_connect()

		# Determine busy/idle state (check whether progress was made during the last daemon cycle)
		if (bridge_isOn()):
			logging.debug("Bridge is ON: Determine busy/idle state")
			if (progress > progressOld):
				logging.debug('Bridge state BUSY: Progress ' + str(progressOld) + ' (' + str(delay) + ' seconds ago) -> ' + str(progress) + ' (now)')
				bridge_setBusy()
			else:
				logging.debug('Bridge state IDLE: Progress ' + str(progressOld) + ' (' + str(delay) + ' seconds ago) -> ' + str(progress) + ' (now)')
				bridge_setIdle()
			progressOld = progress
		else:
			logging.debug("Bridge is OFF")
		
		if (metadata is not False):
			if (bridge_isOn()): 
				logging.info("State: " + str(metadata["state"]) + " (Progress:" + str(metadata["progress"]["completion"]) + ")")
				bridge_update(metadata)
			else:
				logging.debug('Bridge is off -> cannot update metadata')
		else:
			logging.warning("No metadata available")
	except Exception as e: 
		logging.error('Daemon raised exception (' + str(e) + ')')

	logging.debug("Wait for " + str(delay) + 's')
	time.sleep(delay)
