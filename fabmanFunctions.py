# 2019-11-11
# New:
# * added printing_price_per_hour
# * added charge_partial_jobs
# also affected: fabmanConfig.py, /boot/fabman-config.txt
# reboot necessary to add parameters to config.yaml

import json
import requests
from pprint import pprint
import time
import sys
import datetime
from datetime import datetime
import logging
import configparser
import ruamel.yaml
import psutil
import os.path
from os import path

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO) # set level to DEBUG to lo all messages

#octoprint_api_token = '76107D76377D46D29D844CA9A3C839E8'
#octoprint_api_url_base = 'http://localhost/api/'

#fabman_api_token = '8c2b2746-d235-4f7e-b525-9438b52a4c31' # put your fabman bridge api key here!
#fabman_api_url_base = 'https://internal.fabman.io/api/v1/'

configFile = '/boot/fabman-config.txt' # config file in boot partition will be checked at startup of the raspberry pi
yamlFile = '/home/pi/.octoprint/config.yaml'

try:
	yaml = ruamel.yaml.YAML()
	with open(yamlFile) as fp:
		configYaml = yaml.load(fp)
except Exception as e: 
	logging.fatal("Cannot open config file " + yamlFile + " ("  + str(e) + ')')
	sys.exit(0)

try:
	octoprint_api_token = configYaml['plugins']['fabman']['octoprint_api_token']
	octoprint_api_url_base = configYaml['plugins']['fabman']['octoprint_api_url_base']
	fabman_api_token = configYaml['plugins']['fabman']['fabman_api_token']
	fabman_api_url_base = configYaml['plugins']['fabman']['fabman_api_url_base']
	filament_price_per_meter = float(configYaml['plugins']['fabman']['filament_price_per_meter'])
	printing_price_per_hour = float(configYaml['plugins']['fabman']['printing_price_per_hour'])
	charge_partial_jobs = bool(configYaml['plugins']['fabman']['charge_partial_jobs'])
except Exception as e: 
	logging.fatal("Cannot find all parameters in " + yamlFile + " ("  + str(e) + ')')
	sys.exit(0)

#print 'octoprint_api_token: ' + octoprint_api_token
#print 'octoprint_api_url_base: ' + octoprint_api_url_base
#print 'fabman_api_token: ' + fabman_api_token
#print 'fabman_api_url_base: ' + fabman_api_url_base

octoprint_headers = {'Content-Type': 'application/json',
           'X-Api-Key': '{0}'.format(octoprint_api_token)}

fabman_headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(fabman_api_token)}

def bridge_access(mode, emailAddress, metadata=False):
	try:
		api_url = '{0}bridge/access'.format(fabman_api_url_base)
		
		if (mode == 'start'): 
			put_sessionId('0')
			sessionId = '0'
			data = {'emailAddress': emailAddress, 'configVersion': 0}
			reset_idleTime()
			bridge_setIdle()
			logging.info('Bridge started')
		if (mode == 'extend'): 
			logging.debug('mode = extend')
			sessionId = get_sessionId()
			if sessionId == '0': # no open session, therefore nothing to do
				logging.debug('Can\'t extend. No open session.')
				return False
			#pprint (metadata)
			if (metadata == False or metadata["progress"]["completion"] == None): # do not set metadata if no data available
				data = {'emailAddress': emailAddress, 'configVersion': 0, "currentSession": { "id": sessionId } }
				logging.debug("No metadata to set")
			else: # set metadata, if available
				logging.info("Update Metadata")
				#pprint (metadata)
				try:
					data = {'emailAddress': emailAddress, 'configVersion': 0, "currentSession": { "id": sessionId, "metadata": metadata, "charge": create_charge(get_metadata()) } }
				except: # no   data available
					data = {'emailAddress': emailAddress, 'configVersion': 0, "currentSession": { "id": sessionId, "metadata": metadata } }
				
		response = requests.post(api_url, headers=fabman_headers, json=data)
		
		#if response.status_code == 200 and json.loads(response.content.decode('utf-8'))['type'] == "allowed":
		if (response.status_code == 200 and (json.loads(response.content.decode('utf-8'))['type'] == "allowed" or mode == 'extend')):
			put_sessionId(str(json.loads(response.content.decode('utf-8'))["sessionId"]))
			return json.loads(response.content.decode('utf-8'))
		else:
			return False
	except Exception as e: 
		logging.error('Function bridge_access raised exception (' + str(e) + ')')
		return False

def get_sessionId():
	try:
		filename = "/home/pi/fabman/session/fabman.sessionId"
		if (path.exists(filename)):
			f = open(filename, "r")
			return f.read()
		else:
			put_sessionId('0')
			return '0'
	except Exception as e: 
		logging.error('Function get_sessionId raised exception (' + str(e) + ')')
		return False

def put_sessionId(sessionId):
	try:
		f = open("/home/pi/fabman/session/fabman.sessionId", "w")
		f.write(str(sessionId))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function put_sessionId raised exception (' + str(e) + ')')
		return False

def get_printerState():
	try:
		filename = "/home/pi/fabman/session/fabman.printerState"
		if (path.exists(filename)):
			f = open(filename, "r")
			return f.read()
		else:
			put_printerState('OFFLINE')
			return 'OFFLINE'
	except Exception as e: 
		logging.error('Function get_printerState raised exception (' + str(e) + ')')
		return False
		
def put_printerState(printerState):
	try:
		f = open("/home/pi/fabman/session/fabman.printerState", "w")
		f.write(str(printerState))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function put_printerState raised exception (' + str(e) + ')')
		return False

def put_userName(userName): # write username to file for fabmanDaemon.py
	try:
		if (len(sys.argv) == 3):
			f = open("/home/pi/fabman/session/fabman.userName", "w")
			f.write(userName)
			f.close()
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function put_userName raised exception (' + str(e) + ')')
		return False

def get_userName():
	try:
		filename = "/home/pi/fabman/session/fabman.userName"
		if (path.exists(filename)):
			f = open(filename, "r")
			return f.read()
		else:
			put_printerState('')
			return ''
	except Exception as e: 
		logging.error('Function get_userName raised exception (' + str(e) + ')')
		return False

def put_equipmentName(equipmentName): # write equipmentName to file for use in charge description
	try:
		f = open("/home/pi/fabman/session/fabman.equipmentName", "w")
		f.write(str(equipmentName))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function put_equipmentName raised exception (' + str(e) + ')')
		return False
		
def get_equipmentName():
	try:
		f = open("/home/pi/fabman/session/fabman.equipmentName", "r")
		return f.read()
	except Exception as e: 
		logging.error('Function get_equipmentName raised exception (' + str(e) + ')')
		return False

def get_pause():
	try:
		filename = "/home/pi/fabman/session/fabman.pause"
		if (path.exists(filename)):
			f = open(filename, "r")
			ts_pause = int(f.read())
			f.close()
			return ts_pause
		else:
			reset_pause()
			return int(0)
	except Exception as e: 
		logging.error('Function get_pause raised exception (' + str(e) + ')')
		return False

def set_pause():
	try:
		ts = time.time()
		f = open("/home/pi/fabman/session/fabman.pause", "w")
		f.write(str(int(time.time())))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function set_pause raised exception (' + str(e) + ')')
		return False

def reset_pause():
	try:
		ts = time.time()
		f = open("/home/pi/fabman/session/fabman.pause", "w")
		f.write("0")
		f.close()
		return True
	except Exception as e: 
		logging.error('Function reset_pause raised exception (' + str(e) + ')')
		return False

def bridge_setIdle():
	try:
		# if fabman.pause enthält NICHT 0 -> ist bereits Idle -> nichts tun!
		if (get_pause() == 0):
			set_pause()
			logging.info('Set Bridge state to IDLE')
		return True
	except Exception as e: 
		logging.error('Function bridge_setIdle raised exception (' + str(e) + ')')
		return False

def bridge_setBusy():
	try:
		if (get_pause() != 0):
			# calculate duration of pause and add it to fabman.idleTime
			ts_resume = time.time()
			idleTime = int(read_idleTime()) + int(ts_resume - get_pause())
			put_idleTime(idleTime)
			reset_pause()
			logging.info('Set Bridge state to BUSY')
		return True
	except Exception as e: 
		logging.error('Function bridge_setBusy raised exception (' + str(e) + ')')
		return False

def bridge_heartbeat():
	try:
		api_url = '{0}bridge/heartbeat'.format(fabman_api_url_base)
		data = {'configVersion': 0}
		response = requests.post(api_url, headers=fabman_headers, json=data)

		if response.status_code == 200:
			response = json.loads(response.content.decode('utf-8'))
			#pprint(response)
			put_equipmentName(response['config']['name'])
			return response
		else:
			return False
	except Exception as e: 
		logging.error('Function bridge_heartbeat raised exception (' + str(e) + ')')
		return False
		
def get_job_info():
	try:
		api_url = '{0}job'.format(octoprint_api_url_base)
		response = requests.get(api_url, headers=octoprint_headers)

		if response.status_code == 200:
			return json.loads(response.content.decode('utf-8'))
		else:
			return False
	except Exception as e: 
		logging.error('Function get_job_info raised exception (' + str(e) + ')')
		return False

def cancel_job():
	try:
		api_url = '{0}job'.format(octoprint_api_url_base)
		data = {"command" : "cancel"}
		response = requests.post(api_url, headers=octoprint_headers, json=data)
		if response.status_code == 204:
			#send_gcode("M117 Job cancelled")
			#time.sleep(3)
			#send_gcode("M117 Login with Fabman")
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function cancel_job raised exception (' + str(e) + ')')
		return False

def pause_job():
	try:
		api_url = '{0}job'.format(octoprint_api_url_base)
		data = {"command" : "pause", "action" : "pause"}
		response = requests.post(api_url, headers=octoprint_headers, json=data)
		if response.status_code == 204:
			#send_gcode("M117 Job canelled")
			#time.sleep(3)
			#send_gcode("M117 Login with Fabman")
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function pause_job raised exception (' + str(e) + ')')
		return False

def resume_job():
	try:
		api_url = '{0}job'.format(octoprint_api_url_base)
		data = {"command" : "pause", "action" : "resume"}
		response = requests.post(api_url, headers=octoprint_headers, json=data)
		if response.status_code == 204:
			#send_gcode("M117 Job canelled")
			#time.sleep(3)
			#send_gcode("M117 Login with Fabman")
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function resume_job raised exception (' + str(e) + ')')
		return False
		
def send_gcode(gcode):
	try:
		api_url = '{0}printer/command'.format(octoprint_api_url_base)
		data = {"command" : gcode}
		response = requests.post(api_url, headers=octoprint_headers, json=data)
		#pprint(response)
		if response.status_code == 204:
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function send_gcode raised exception (' + str(e) + ')')
		return False

def put_idleTime(idleTime):
	try:
		ts = time.time()
		f = open("/home/pi/fabman/session/fabman.idleTime", "w")
		f.write(str(idleTime))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function put_idleTime raised exception (' + str(e) + ')')
		return False

def reset_idleTime():
	try:
		put_idleTime(0)
		return True
	except Exception as e: 
		logging.error('Function reset_idleTime raised exception (' + str(e) + ')')
		return False

def read_idleTime(): # reads value from file fabman.idleTime
	try:
		f = open("/home/pi/fabman/session/fabman.idleTime", "r")
		idle_time = int(f.read())
		return idle_time
	except Exception as e: 
		logging.error('Function get_idleTime raised exception (' + str(e) + ')')
		return False

def get_idleTime(): # reads value from file fabman.idleTime and adds current pause
	try:
		if (bridge_isOn()):
			idle_time = read_idleTime()
			if (bridge_isIdle()): # if state is currently idle, then add time since pause started
				ts_pause = get_pause()
				#print "pause = " + str(ts_pause)
				idle_time += (int(time.time()) - int(get_pause()))
				#print "idle =  " + str(idle_time)
			return idle_time
		else:
			return 0
	except Exception as e: 
		logging.error('Function get_idleTime raised exception (' + str(e) + ')')
		return False

def get_totalTime():
	try:
		if (bridge_isOn()):
			ts_now = int(time.time())
			ts_start = get_start()
			total_time = ts_now - ts_start
			return total_time
		else:
			return 0
	except Exception as e: 
		logging.error('Function get_totalTime raised exception (' + str(e) + ')')
		return False

def get_busyTime():
	try:
		if (bridge_isOn()):
			return (get_totalTime() - get_idleTime())
		else:
			return 0
	except Exception as e: 
		logging.error('Function get_busyTime raised exception (' + str(e) + ')')
		return False
		
def octoprint_connect():
	try:
		time.sleep(3) # wait a bit until avrdude is running in case of disconnect because of firmware flasher plugin
		if ("avrdude" in (p.name() for p in psutil.process_iter())):
			logging.info('Connect aborted because avrdude is running (firmware flasher)')
		else:
			api_url = '{0}connection'.format(octoprint_api_url_base)
			data = {"command" : "connect"}
			response = requests.post(api_url, headers=octoprint_headers, json=data)
			if response.status_code == 204:
				return True
			else:
				return False
	except Exception as e: 
		logging.error('Function octoprint_connect raised exception (' + str(e) + ')')
		return False

def octoprint_disconnect():
	try:
		api_url = '{0}connection'.format(octoprint_api_url_base)
		data = {"command" : "disconnect"}
		response = requests.post(api_url, headers=octoprint_headers, json=data)
		if response.status_code == 204:
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function octoprint_disconnect raised exception (' + str(e) + ')')
		return False

def octoprint_reconnect():
	try:
		octoprint_disconnect()
		octoprint_connect()
		return True
	except Exception as e: 
		logging.error('Function octoprint_reconnect raised exception (' + str(e) + ')')
		return False

def get_octoprint_settings():
	try:
		api_url = '{0}settings'.format(octoprint_api_url_base)
		response = requests.get(api_url, headers=octoprint_headers)

		if response.status_code == 200:
			return json.loads(response.content.decode('utf-8'))
		else:
			return False
	except Exception as e: 
		logging.error('Function get_octoprint_settings raised exception (' + str(e) + ')')
		return False

def get_metadata():
	global filament_price_per_meter
	global printing_price_per_hour
	try:
		metadata = get_job_info()
		# costestimation plugin wird nicht mehr verwendet
		#metadata['costestimation'] = get_octoprint_settings()['plugins']['costestimation']
		if (filament_price_per_meter > 0.0 or printing_price_per_hour > 0.0):
			metadata['charge'] = create_charge(metadata)
		return metadata
	except Exception as e: 
		logging.error('Function get_metadata raised exception (' + str(e) + ')')
		return False

'''
def create_charge_costestimation(metadata): # based on Plugin Cost Estimation
	try:
		#seconds = metadata['job']['estimatedPrintTime'] # charge according to estimated print time
		#seconds = float(metadata['progress']['printTime']) + float(metadata['progress']['printTimeLeft']) # charge according to dynamically adjusted time estimation (from plugin "genius")
		seconds = float(metadata['progress']['printTime']) / float(metadata['progress']['completion']) * 100.0 # charge according to dynamically adjusted time estimation (from plugin "genius")
		if (seconds == None):
			seconds = 0
	except Exception as e: 
		logging.info("No job duration available -> set seconds to 0")
		seconds = 0
	try:
		ccm = metadata['job']['filament']['tool0']['volume']
	except Exception as e: 
		logging.debug("cannot fetch volume data in metadata for charging -> set ccm to 0 ("  + str(e) + ')')
		ccm = 0
		
	try:
		completion = metadata['progress']['completion']
		if (completion == None):
			completion = 0.0
		#print completion
		costOfFilament = float(metadata['costestimation']['costOfFilament'])
		weightOfFilament = float(metadata['costestimation']['weightOfFilament'])
		densityOfFilament = float(metadata['costestimation']['densityOfFilament'])
		#diameterOfFilament = float(metadata['costestimation']['diameterOfFilament'])

		if (densityOfFilament > 0):
			filamentCost = ccm / (weightOfFilament/densityOfFilament) * costOfFilament
			#print filamentCost
		else:
			#print "Division by Zero (filamentCost)"
			logging.debug('densityOfFilament is not set -> set filamentCost to 0')
			filamentCost = 0.0

		costOfElectricity = float(metadata['costestimation']['costOfElectricity'])
		powerConsumption = float(metadata['costestimation']['powerConsumption'])
		timebasedCost = float(seconds)/3600 * powerConsumption * costOfElectricity

		maintenanceCosts = float(metadata['costestimation']['maintenanceCosts'])
		lifespanOfPrinter = float(metadata['costestimation']['lifespanOfPrinter'])
		priceOfPrinter = float(metadata['costestimation']['priceOfPrinter'])
		if (lifespanOfPrinter > 0 and maintenanceCosts > 0):
			printerCost = (seconds / (lifespanOfPrinter*3600) * priceOfPrinter) + (seconds/3600 * maintenanceCosts)
			#print printerCost
		else:
			#print "Division by Zero (printerCost)"
			logging.debug('lifespanOfPrinter and/or maintenanceCosts is not set -> set printerCost to 0')
			printerCost = 0.0
		
		price = (filamentCost + timebasedCost + printerCost) * (completion/100)
		
		#description = 'Print job "' + str(metadata['job']['file']['name']) + '" on ' + get_equipmentName() + ' (' + str(int(round(seconds))) + 's / ' + str(round(ccm,2)) + 'ccm / ' + str(round(completion,2)) + '% completed)'
		description = 'Print job "' + str(metadata['job']['file']['name']) + ' (' + str(int(round(seconds))) + 's / ' + str(round(ccm,2)) + 'ccm / ' + str(round(completion,2)) + '% completed)'
		charge = {'price' : price, 'description': description }
		return charge
	except Exception as e: 
		logging.error('Function create_charge raised exception (' + str(e) + ')')
		return False
'''

def create_charge(metadata): # based on filament usage or time (price set in /boot/fabman-config.txt)
	global filament_price_per_meter
	global printing_price_per_hour
	global charge_partial_jobs

	try:
		meter = float(metadata['job']['filament']['tool0']['length'])/1000
	except Exception as e: 
		logging.debug("cannot fetch volume data (job/filament/tool0/length) in metadata for charging -> set meter to 0 ("  + str(e) + ')')
		meter = 0.0
		
	try:
		completion = metadata['progress']['completion']
		if (completion == None):
			completion = 0.0
		else:
			completion = float(completion)
		
		meter = meter * completion/100
		seconds = get_busyTime()
		priceFilament = meter * filament_price_per_meter
		priceTime = float(seconds) * printing_price_per_hour/3600
		price = priceFilament + priceTime
		
		if (charge_partial_jobs == False and completion != 100):
			price = 0
		
		description = 'Print job "' + str(metadata['job']['file']['name']) + '" ' + str(round(completion,2)) + '% completed (' + str(round(meter,2)) + 'm filament / ' + str(seconds) + 's print time)' 
		charge = {'price' : price, 'description': description }
		return charge
	except Exception as e: 
		logging.error('Function create_charge raised exception (' + str(e) + ')')
		return False
		
def fabmanConfig(sectionName, parameterName):
	global configFile
	global yamlFile

	try:
		# open config file
		fabmanConfig = configparser.ConfigParser()
		fabmanConfig.read(configFile)

		# open yaml file
		yaml = ruamel.yaml.YAML()
		yaml.preserve_quotes = False
		with open(yamlFile) as fp:
			configYaml = yaml.load(fp)
	except Exception as e: 
		logging.info('Function fabmanConfig raised exception (' + str(e) + ')')
		return False
	
	if (sectionName == 'octoprint-fabman-auth'):
		yamlSection = 'accessControl'
		yamlSubsection = 'fabman'
	if (sectionName == 'fabman'):
		yamlSection = 'plugins'
		yamlSubsection = 'fabman'
	'''
	try:
		configYaml['plugins']['fabman']
	except Exception as e: 
		configYaml[yamlSection].update( { 'fabman' : { } } )
	'''		
	try:
		fabmanConfig[sectionName][parameterName]
		src = True
	except Exception as e: 
		src = False
	try:
		configYaml[yamlSection][yamlSubsection][parameterName]
		dst = True
	except Exception as e: 
		dst = False

	#print fabmanConfig[sectionName][parameterName].split(",")
	#print str(configYaml[yamlSection][yamlSubsection][parameterName])

	try:
		if (sectionName == 'bridge' and parameterName == 'name'):
			bridgeName = str(bridge_heartbeat()['config']['name'])
			if (configYaml['appearance']['name'] == bridgeName):
				logging.debug('Value ' + parameterName + ' is already up to date: ' + bridgeName)
			else:
				logging.info('Update ' + parameterName + ' in ' + yamlFile + ' from ' + str(configYaml['appearance']['name']) + ' to ' + bridgeName)
				configYaml['appearance']['name'] = bridgeName
		else:
			if (src):
				if (dst):
					# UPDATE Parameter
					if (parameterName == 'resourceIds'): # list of values expected (comma-separated)
						list = [int(e) if e.isdigit() else e for e in fabmanConfig[sectionName][parameterName].split(',')]
						#pprint (list)
						if (sorted(list) != sorted(configYaml['accessControl']['fabman']['resourceIds'])):
							logging.info('Update ' + parameterName + ' in ' + yamlFile + ' from ' + ",".join(str(v) for v in configYaml[yamlSection][yamlSubsection][parameterName]) + ' to ' + ",".join(str(v) for v in list))
							# wert in config yaml überschreiben
							configYaml[yamlSection][yamlSubsection][parameterName] = list
						else:
							logging.debug('Value ' + parameterName + ' is already up to date: ' + ",".join(str(v) for v in configYaml[yamlSection][yamlSubsection][parameterName]))
					else: # single value
						if (str(fabmanConfig[sectionName][parameterName]).lower() != str(configYaml[yamlSection][yamlSubsection][parameterName]).lower()):
							logging.info('Update ' + parameterName + ' in ' + yamlFile + ' from ' + str(configYaml[yamlSection][yamlSubsection][parameterName]) + ' to ' + str(fabmanConfig[sectionName][parameterName]))
							# wert in config yaml überschreiben
							if (parameterName in ('accountId')): # integer values
								configYaml[yamlSection][yamlSubsection][parameterName] = int(fabmanConfig[sectionName][parameterName])
							elif (parameterName in ('allowLocalUsers','enabled','restrictAccess','charge_partial_jobs')): # boolean values
								if (fabmanConfig[sectionName][parameterName].lower() == 'false'): 
									configYaml[yamlSection][yamlSubsection][parameterName] = False
								else:
									configYaml[yamlSection][yamlSubsection][parameterName] = True
							else: # string values
								configYaml[yamlSection][yamlSubsection][parameterName] = fabmanConfig[sectionName][parameterName]
						else:
							# Parameter is up to date
							logging.debug('Value ' + parameterName + ' is already up to date: ' + str(configYaml[yamlSection][yamlSubsection][parameterName]))
				else:
					# ADD Parameter
					logging.info('Add ' + parameterName + ' with value ' + str(fabmanConfig[sectionName][parameterName]) + ' to ' + yamlFile)
					configYaml[yamlSection][yamlSubsection].update( { parameterName : str(fabmanConfig[sectionName][parameterName]) } )
			else:
				logging.info("Skip parameter " + parameterName + ' (not found in ' + configFile + ')')

		# write new config.yaml
		with open(yamlFile, 'w') as outfile:
			yaml.dump(configYaml, outfile)	
			outfile.close()
		return configYaml

	except Exception as e: 
		logging.info('Function fabmanConfig raised exception (' + str(e) + ')')

def bridge_start(userName):
#if (sys.argv[1] == 'start'):
	response = bridge_access('start', userName) # Parameter: 'start', <username>
	put_userName(userName)
	set_start()
	#pprint(response)
		
	if (response == False): # access failed, e.g. user has no permission
		# cancel print
		logging.info('No permission to print -> cancel job')
		cancel_job()
		send_gcode("M117 Access denied!")
		time.sleep(5)
		send_gcode("M117 Login with Fabman")
	else:
		# start in idle-mode (waiting for user to press knob)
		reset_pause()
		bridge_setIdle()
		
		#send_gcode("M1 Press knob ...") # hat nicht fortgesetzt bei knopfdruck, daher: configured in gui -> Settings / GCODE Scritps / Before print job starts 
		
def bridge_extend(userName, metadata=False):
#if (sys.argv[1] == 'extend'):
	#response = bridge_access('extend', userName) # Parameter: 'extend', <username>
	put_userName(userName)
	#pprint(response)

	if (bridge_access('extend', userName, metadata)): # bridge is on (bridge session active)
		#update_metadata(metadata)
		''' ######## busy/idle detection wird jetzt von daemon gemacht ############
		if (metadata["state"][0:8] == "Printing" and metadata["progress"]["printTime"] > 0): # bridge state "busy": printing has started (made progress already)
			logging.debug("Fabman Bridge is ON (BUSY)")
			#send_gcode("M117 Fabman Bridge busy")
			bridge_setBusy()
		else: # bridge state "idle": not printing
			logging.debug("Fabman Bridge is ON (IDLE)")
			#send_gcode("M117 Fabman Bridge idle")
			bridge_setIdle()		
		'''
	else: # bridge is off
		#send_gcode("M117 Fabman Bridge off")
		logging.debug("Fabman Bridge is OFF")

def bridge_stop(): 
	try:
		sessionId = get_sessionId()
		idleTime = get_idleTime()
		metadata = get_metadata()
		
		#bridge_setBusy() # to add last idle period before stopping the bridge
		reset_pause()
		
		api_url = '{0}bridge/stop'.format(fabman_api_url_base)
		
		if (metadata == False or metadata["progress"]["completion"] == None): # do not set metadata if no data available
			data = { "stopType": "normal", "currentSession": { "id": sessionId, "idleDurationSeconds": idleTime } }
		else: # set metadata, if available
			try:
				data = { "stopType": "normal", "currentSession": { "id": sessionId, "idleDurationSeconds": idleTime, "metadata": metadata, "charge": create_charge(get_metadata()) } }
			except: # no charge data available
				data = { "stopType": "normal", "currentSession": { "id": sessionId, "idleDurationSeconds": idleTime, "metadata": metadata } }
		#pprint(data)
		response = requests.post(api_url, headers=fabman_headers, json=data)

		if response.status_code == 200 or response.status_code == 204:
			put_sessionId('0') # no session
			reset_idleTime()
			logging.info('Bridge stopped successfully')
			return True
		else:
			logging.warning('Could not stop Bridge (no open session)')
			return False
	except Exception as e: 
		logging.error('Function bridge_stop raised exception (' + str(e) + ')')
		return False


def bridge_update(metadata): 
	try:
		sessionId = get_sessionId()
		#metadata = get_metadata()
		idleTime = int(get_idleTime())
		#ts_pause = int(get_pause())
		#if (ts_pause != 0): # bridge is currently idle
		#	ts_now = int(time.time())
		#	idleTime = idleTime + (ts_now - ts_pause)
		
		api_url = '{0}bridge/update'.format(fabman_api_url_base)
		
		if (metadata == False or metadata["progress"]["completion"] == None): # do not set metadata if no data available
			data = { "session": { "id": sessionId, "idleDurationSeconds": idleTime } }
		else: # set metadata, if available
			try:
				data = { "session": { "id": sessionId, "idleDurationSeconds": idleTime, "metadata": metadata, "charge": create_charge(get_metadata()) } }
			except: # no charge data available
				data = { "session": { "id": sessionId, "idleDurationSeconds": idleTime, "metadata": metadata } }
		#pprint(data)
		response = requests.post(api_url, headers=fabman_headers, json=data)

		if response.status_code == 200 or response.status_code == 204:
			logging.info('Bridge data (metadata/charge) updated successfully')
			#pprint(response)
			return True
		else:
			logging.warning('Could not update bridge data (metadata/charge)')
			return False
	except Exception as e: 
		logging.error('Function bridge_update raised exception (' + str(e) + ')')
		return False

		
################### NEUE FUNKTONEN #####################
def bridge_isOn():
	if (int(get_sessionId()) != 0):
		return True
	else:
		return False

def bridge_isOff():
	if (int(get_sessionId()) == 0):
		return True
	else:
		return False

def bridge_isIdle():
	if (int(get_sessionId()) != 0 and int(get_pause()) != 0):
		return True
	else:
		return False

def bridge_isBusy():
	if (int(get_sessionId()) != 0 and int(get_pause()) == 0):
		return True
	else:
		return False

def get_start():
	try:
		filename = "/home/pi/fabman/session/fabman.start"
		if (path.exists(filename)):
			f = open(filename, "r")
			ts_start = int(f.read())
			f.close()
			return ts_start
		else:
			reset_start()
			return int(0)
	except Exception as e: 
		logging.error('Function get_start raised exception (' + str(e) + ')')
		return False

def set_start():
	try:
		f = open("/home/pi/fabman/session/fabman.start", "w")
		f.write(str(int(time.time())))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function set_start raised exception (' + str(e) + ')')
		return False

def reset_start():
	try:
		f = open("/home/pi/fabman/session/fabman.start", "w")
		f.write("0")
		f.close()
		return True
	except Exception as e: 
		logging.error('Function reset_start raised exception (' + str(e) + ')')
		return False



