exec(open("/home/pi/fabman/fabmanFunctions.py").read())

# verhindern, dass daemon zweimal gestartet wird
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

#logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
#logging.warning('This will get logged to a file')
#logging.debug('Daemon started')

try:
	logging.info("Starting daemon")
	delay = 30
	# stop bridge, if still running
	#response = bridge_stop(get_sessionId(), get_idleTime(), get_metadata())
	#response = bridge_stop()
	#reset_pause()
	
except Exception as e: 
	logging.error('Initialization of Daemon raised exception (' + str(e) + ')')
	
try:
	metadata = get_metadata()
	progressOld = float(metadata["progress"]["completion"])
except:
	#logging.info('No progress data available: set progress to 0')
	progressOld = 0.0

while 1:
	try:
		metadata = get_metadata()
		progress = float(metadata["progress"]["completion"])
	except:
		logging.debug('No progress data available: set progress to 0')
		progress = 0.0

	try:
		logging.debug("Heartbeat")
		bridgeData = bridge_heartbeat() 

		# Determine busy/idle state (check whether progress was made during the last daemon cycle)
		if (get_sessionId() != '0'): # if bridge is on
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
		'''
		# update bridge name for display in octoprint ui header (restart of octoprint necessary to take effect) -> NICHT MEHR: kann man über die settings in UI machen
		bridgeName = bridgeData['config']['name']
		# open yaml file
		yaml = ruamel.yaml.YAML()
		yaml.preserve_quotes = False
		with open(yamlFile) as fp:
			configYaml = yaml.load(fp)
		if (configYaml['appearance']['name'] == bridgeName):
			logging.debug('Value appearance/name is already up to date: ' + bridgeName)
		else:
			logging.info('Update appearance/name in ' + yamlFile + ' from ' + str(configYaml['appearance']['name']) + ' to ' + bridgeName)
			configYaml['appearance']['name'] = bridgeName
		# write new config.yaml
		with open(yamlFile, 'w') as outfile:
			yaml.dump(configYaml, outfile)	
			outfile.close()
		'''
		
		#metadata = get_metadata()
		if (metadata is not False):
			if (str(metadata["state"][0:7]) == "Offline" or str(metadata["state"][0:5]) == "Error"):
				octoprint_connect()
			#pprint(metadata)
			if metadata is not False: 
				logging.info("State: " + str(metadata["state"]) + " (Progress:" + str(metadata["progress"]["completion"]) + ")")
				##########################################
				# bridge_extend vorübergehend deaktiviert
				logging.debug("Bridge extend deactivated")
				#bridge_extend(get_userName(), metadata)
				##########################################
				# stattdessen neu /bridge/update
				bridge_update(metadata)
			else:
				logging.error('get_metadata: Request Failed')
		else:
			logging.warning("No metadata available")
		#sys.exit()
	except Exception as e: 
		logging.error('Daemon raised exception (' + str(e) + ')')

	logging.debug("Wait for " + str(delay) + 's')
	time.sleep(delay)
