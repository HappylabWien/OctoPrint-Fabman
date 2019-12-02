OctoPrint-Fabman
================

Introduction
------------

I'd like to share my experiments with connecting [OctoPrint](https://octoprint.org/) to [Fabman](https://fabman.io) without the need for a Fabman bridge. **The implementation is in a very early stage and not yet tested a lot.**

To implement this you need:

- Prusa MK3 printer
- Raspberry PI 3
- Micro SD card (min. 8GB)
- Fabman Account (you can get your free trial account [here](https://fabman.io))
- WiFi and Internet connection

### What is Fabman?

[Fabman](https://fabman.io) is an all-in-one makerspace management solution. It is the "operating system" for makerspaces, fab labs, coworking spaces or school workshops. It helps to manage machines and members easily, safely & efficiently.

### Why OctoPrint?

OctoPrint is a very powerful web-based tool to manage 3d printers. It's 100% open source and supports a [wide range of 3d printers](https://github.com/foosel/OctoPrint/wiki/Supported-Printers) - including Prusa, RepRap, Ultimaker, etc. So, if we support Octoprint, we immediately support all of them.

### Why connect 3D printers to Fabman?

The main features and advantages of this configuration are:

- ***Permission management:*** You can control via Fabman who is allowed to print
- ***Logging:*** You see all your printing activities at one sight in the Fabman dashboard
- ***Billing:*** You can automatically charge according to actual usage of the printer. Time and filament based charges are supported.

### How to use the OctoPrint with Fabman?

In our approach you simply login to your OctoPrint installation with the login data you use for the Fabman member portal. Thanks to our colleagues at Fab Lab Brno! They published a [Plugin für OctoPrint authentication against Fabman](https://github.com/rplnt/octoprint-fabman-auth). We've used it for this part.

You can then upload your 3d print file (GCODE file) and send it to the printer. Then confirm to start by pressing the knob directly at the printer. Now the job starts and you can immediately see it on the Fabman dashboard. When the print is finished, it will be automatically charged according your pricing settings in Fabman.

Installation Guide
------------------

### Install the adapted OctoPi image on the SD card

As soon as I find time I’ll write a more detailed documentation. You can [download the image](https://drive.google.com/file/d/1fgGlbhjOgSsZBqq6AhLT7e_BjqS5w5e3/view?usp=sharing) (zip-file, ca. 7 GB) and flash it on an SD card. Therefore, ***follow the instructions 1. to 5. in Section “Setting up OctoPi” [here](https://octoprint.org/download/)***. Use the image mentioned above instead of the image provided on the OctoPi website.

### Configure your installation

#### Fabman Configuration
- Set your Fabman Bridge API key. If it doesn’t yet exist, create a new equipment (type 3D printer) in Fabman and create an API key for it. 
- Do not set time based costs in the equipment details in Fabman. Configuration for billing, time or filament based, will be described below.

#### Configuration prior to the first boot of OctoPrint

With the SD card plugged in to your computer (you may need an adapter for your computer to accept the SD card if it doesn't already include the appropriate slot). You access the card just as you would an external disk or thumb drive mounted on your computer. The files you will need to edit are in the /boot/ directory of the SD card (if you are editing on a Windows or Mac computer, the /boot/ directory will likely be the only directory you can see.) Look in the "boot" directory of the SD card. ***If you are on a Windows computer do not use the standard editor, as it cannot deal properly with Unix formatted files. Use e.g. Notepad++, which is freely available for download.***

#### Configure WIFI
In the /boot/ directory, open `octopi-wpa-supplicant.txt`, search for the following section and enter your Wifi parameters:
```
## WPA/WPA2 secured
network={
  ssid="YOUR_WIFI_SSID"
  psk="YOUR_WIFI_PASSWORD"
}
```
### Set hostname
In the `/boot` directory, open `octopi-hostname.txt` (or add it, if the file does not exist) and enter your hostname as the first (and only) line of the file, e.g.:
```
printer
```
You can access the OctoPrint service afterwards from a web browser within the wifi via the following url:
`http://printer.local` (Bonjours service must be supported on the client)

#### Set Fabman data
In the `/boot` directory, open `fabman-config.txt` and enter your Fabman connection data. Here is an example:
```
[octoprint-fabman-auth]
accountId = 1
allowLocalUsers = true
enabled = true
resourceIds = 893
restrictAccess = true
url = https://fabman.io/api/v1/

[fabman] 
octoprint_api_token = 76107D76377D46D29D844CA9A3C839E8
octoprint_api_url_base = http://localhost/api/
fabman_api_token = 8c2b2746-d235-4f7e-b525-9438b52a4c22
fabman_api_url_base = https://fabman.io/api/v1/
filament_price_per_meter = 0.55
printing_price_per_hour = 1.2
charge_partial_jobs = true
```
The following values have to be set according to your installation:
- `[octoprint-fabman-auth]` / `accountId` and `resourceIds`: Login to your Fabman account. Go to Configure / Equipment and select the 3D printer. You find the data in the URL (https://fabman.io/manage/<accountId>/configuration/resources/<resourceId>
- `[fabman]` / `fabman_api_token`: Find [here](https://help.fabman.io/article/32-create-a-bridge-api-key) how to create the API token
- `[fabman]` / `filament_price_per_meter`: If you plan to charge according to filament used, set the price per meter here. If you do not need this feature, set the price to `0` (do not delete the parameter).
- `[fabman]` / `printing_price_per_hour`:  If you plan to charge according to printing time, set the price per hour here. Heat up time or pauses are not counted. If you do not need this feature, set the price to `0` (do not delete the parameter).
- `[fabman]` / `Charge_partial_jobs`: Set `true`, if you want to charge uncompleted/cancelled jobs aliquotely. Set `false`, if only 100% completed job shall be charged.

#### Octoprint Settings
Connect the Raspberry Pi via USB to the Prusa printer, insert the SD card into the Raspberry Pi card slot, and power it on. It can take a few minutes to boot completely.

Login to OctoPrint via your web browser (`http://<ip address>`). Access OctoPrint from a web browser on your network by navigating to any of:
    `http://printer.local` (depends on the name you have set in `/boot/hostname.txt` before first boot)
    `http://<ip-address>` (How to [find out the IP address](https://community.octoprint.org/t/finding-the-pis-ip-address/844))

The default OctoPrint login is username `admin` / password `admin`. Change the password in the user settings. 

Go to `Settings / Appearance` to set the name of your printer. This name is displayed in the top left corner of the screen. This is particularly important if you run several printers to avoid confusion.

If needed, enable/configure the following Plugins:
- Auto Logout
- Force Login
- Delete After Print
A restart of OctoPrint might be necessary to activate the changes.

#### Change Raspberry Pi Password

For security reasons you are strongly advised to change the password of the default user on your Raspberry Pi according to this [Howto](https://www.theurbanpenguin.com/raspberry-pi-changing-the-default-users-password-and-creating-addtional-accounts/).

Keep your Installation up to date
---------------------------------
- Login to your Raspberry Pi via ssh (user pi)
- go to the fabman directory: `cd /home/pi/fabman`
- get newest version: `git pull origin master`
- restart octoprint: `sudo service octoprint restart` (you will be asked for the password of the user pi)

How to Start a Print Job
------------------------

1. Open a web browser and go to [`http://printer.local`](http://printer.local)  (use here the server name you have set in `/boot/octopi-hostname.txt`) and log in with the username (email address) and password of the Fabman Member Portal
2. Upload the GCODE file - created with the [PrusaSlicer](https://www.prusa3d.com/prusaslicer/)
3. Click the Printer-Icon in the List to send the job to the printer. After the beep, start printing directly at the printer by pressing the knob.

![OctoPrint-Screenshot](OctoPrint-Screenshot.png)
