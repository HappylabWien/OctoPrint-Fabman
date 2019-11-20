# 2019-11-15
# New:
# * tidy up code
# * state update in metadata when job finished
# * add pricing settings to metadata
# * write metadata immediately after start

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

octoprint_headers = {'Content-Type': 'application/json',
           'X-Api-Key': '{0}'.format(octoprint_api_token)}

fabman_headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(fabman_api_token)}

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

def get_equipmentName():
	try:
		f = open("/home/pi/fabman/session/fabman.equipmentName", "r")
		return f.read()
	except Exception as e: 
		logging.error('Function get_equipmentName raised exception (' + str(e) + ')')
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
		
def get_pause():
	try:
		filename = "/home/pi/fabman/session/fabman.pause"
		if (path.exists(filename)):
			f = open(filename, "r")
			ts_pause = int(f.read())
			f.close()
			return ts_pause
		else:
			put_pause("0")
			return int(0)
	except Exception as e: 
		logging.error('Function get_pause raised exception (' + str(e) + ')')
		return False

def put_pause(pause = int(time.time())): # put_pause(0) to reset pause
	try:
		f = open("/home/pi/fabman/session/fabman.pause", "w")
		f.write(str(pause))
		f.close()
		return True
	except Exception as e: 
		logging.error('Function put_pause raised exception (' + str(e) + ')')
		return False

def bridge_setIdle():
	try:
		if (bridge_isBusy()):
			put_pause()
			logging.info('Set Bridge state to IDLE')
		return True
	except Exception as e: 
		logging.error('Function bridge_setIdle raised exception (' + str(e) + ')')
		return False

def bridge_setBusy():
	try:
		if (bridge_isIdle()):
			put_idleTime(get_idleTime())
			put_pause("0")
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

def get_idleTime(): # reads value from file fabman.idleTime and adds current pause
	try:
		if (bridge_isOn()):
			f = open("/home/pi/fabman/session/fabman.idleTime", "r")
			idle_time = int(f.read())
			if (bridge_isIdle()): # if state is currently idle, then add time since pause started
				idle_time += (int(time.time()) - int(get_pause()))
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
	global charge_partial_jobs
	try:
		metadata = get_job_info()
		metadata['state'] = get_printerState()
		metadata['pricing'] = { 'filament_price_per_meter' : filament_price_per_meter,
								'printing_price_per_hour' : printing_price_per_hour,
								'charge_partial_jobs' : charge_partial_jobs }
		if (filament_price_per_meter > 0.0 or printing_price_per_hour > 0.0):
			metadata['charge'] = create_charge(metadata)
		return metadata
	except Exception as e: 
		logging.error('Function get_metadata raised exception (' + str(e) + ')')
		return False

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
		
		description = 'Print job "' + str(metadata['job']['file']['name']) + '" ' + str(round(completion,2)) + '% completed ('
		if ((filament_price_per_meter > 0) or (meter > 0)):
			description += str(round(meter,2)) + 'm filament / '
		description += str(seconds) + 's print time)' 
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
	try:
		put_sessionId('0')
		sessionId = '0'
		reset_idleTime()

		api_url = '{0}bridge/access'.format(fabman_api_url_base)
		data = {'emailAddress': userName, 'configVersion': 0}
		response = requests.post(api_url, headers=fabman_headers, json=data)

		put_userName(userName)
		set_start()
		
		if (response.status_code == 200 and json.loads(response.content.decode('utf-8'))['type'] == "allowed"):
			logging.info('Bridge started')
			put_sessionId(str(json.loads(response.content.decode('utf-8'))["sessionId"]))
			response = json.loads(response.content.decode('utf-8'))

			# start in idle-mode (waiting for user to press knob)
			put_pause("0")
			bridge_setIdle()
			
			#bridge_update(get_metadata())

		else: # access failed, e.g. user has no permission
			logging.info('Bridge could not be started (access denied)')

			# cancel print
			logging.info('No permission to print -> cancel job')
			cancel_job()
			send_gcode("M117 Access denied!")
			time.sleep(5)
			send_gcode("M117 Login with Fabman")

	except Exception as e: 
		logging.error('Function bridge_start raised exception (' + str(e) + ')')
		return False

def bridge_stop(): 
	try:
	
		if (bridge_isOff()): # do nothing if bridge is off already
			logging.debug('Bridge could not be stopped (is off already)')
			return False
			
		sessionId = get_sessionId()
		idleTime = get_idleTime()
		metadata = get_metadata()
		
		#bridge_setBusy() # to add last idle period before stopping the bridge
		put_pause("0")
		
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
		idleTime = int(get_idleTime())
		
		api_url = '{0}bridge/update'.format(fabman_api_url_base)
		
		if (metadata == False): # do not set metadata if no data available
			data = { "session": { "id": sessionId, "idleDurationSeconds": idleTime } }
		else: # set metadata, if available
			try:
				data = { "session": { "id": sessionId, "idleDurationSeconds": idleTime, "metadata": metadata, "charge": create_charge(get_metadata()) } }
			except: # no charge data available
				data = { "session": { "id": sessionId, "idleDurationSeconds": idleTime, "metadata": metadata } }
		response = requests.post(api_url, headers=fabman_headers, json=data)

		if response.status_code == 200 or response.status_code == 204:
			logging.debug('Bridge data (metadata/charge) updated successfully')
			return True
		else:
			logging.warning('Could not update bridge data (metadata/charge)')
			return False
	except Exception as e: 
		logging.error('Function bridge_update raised exception (' + str(e) + ')')
		return False
		
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

def printer_isOffline(metadata):
	try:
		if (str(metadata["state"][0:7]).upper() == "OFFLINE" or str(metadata["state"][0:5]).upper() == "ERROR"):
			return True
		else:
			return False
	except Exception as e: 
		logging.error('Function printer_isOffline raised exception (' + str(e) + ')')
		return False

