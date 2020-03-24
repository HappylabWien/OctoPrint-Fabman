exec(open("/home/pi/fabman/fabmanFunctions.py").read())
	
logging.info("Check config file " + configFile)

fabmanConfig('octoprint-fabman-auth', 'accountId')
fabmanConfig('octoprint-fabman-auth', 'allowLocalUsers')
fabmanConfig('octoprint-fabman-auth', 'enabled')
fabmanConfig('octoprint-fabman-auth', 'resourceIds') # ACHTUNG Liste!!!!
fabmanConfig('octoprint-fabman-auth', 'restrictAccess')
fabmanConfig('octoprint-fabman-auth', 'url')

fabmanConfig('fabman', 'octoprint_api_token')
fabmanConfig('fabman', 'octoprint_api_url_base')
fabmanConfig('fabman', 'fabman_api_token')
fabmanConfig('fabman', 'fabman_api_url_base')

fabmanConfig('fabman', 'filament_price_per_meter')
fabmanConfig('fabman', 'printing_price_per_hour')
fabmanConfig('fabman', 'min_price_per_job')
fabmanConfig('fabman', 'charge_partial_jobs')

#fabmanConfig('bridge', 'name') # geht beim boot noch nicht, da namensauflösung noch nicht funktioniert; wird daher im daemon gemacht.
