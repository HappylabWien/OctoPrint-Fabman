OctoPrint-Fabman
================

Introduction
------------

I'd like to share my experiments with connecting [OctoPrint](https://octoprint.org/) to [Fabman](https://fabman.io) without the need for a Fabman bridge. **The implementation is in a very early stage and not yet tested a lot.**

To implement this you need:

- Prusa MK3 printer
- Raspberry PI 3
- Micro SD card (min. 8GB)
- Fabman Account (you can get your free trial account here)
- WiFi and Internet connection

### What is Fabman?

[Fabman](https://fabman.io) is an all-in-one makerspace management solution. It is the "operating system" for makerspaces, fab labs, coworking spaces or school workshops. It helps to manage machines and members easily, safely & efficiently.

### Why OctoPrint?

OctoPrint is a very powerful web-based tool to manage 3d printers. It's 100% open source and supports a [wide range of 3d printers](https://github.com/foosel/OctoPrint/wiki/Supported-Printers) - including Prusa, RepRap, Ultimaker, etc. So, if we support Octoprint, we immediately support all of them.

### Why connect 3D printers to Fabman?

The main features and advantages of this configuration are:

- Permission management: You can control via Fabman who is allowed to print
- Logging: You see all your printing activities at one sight in the Fabman dashboard
- Billing: You can automatically charge according to actual usage of the printer. Time and filament based charges are supported.

### How to use the OctoPrint with Fabman?

In our approach you simply login to your OctoPrint installation with the login data you use for the Fabman member portal. Thanks to our colleagues at Fab Lab Brno! They published a [Plugin für OctoPrint authentication against Fabman](https://github.com/rplnt/octoprint-fabman-auth). We've used it for this part.

You can then upload your 3d print file (GCODE file) and send it to the printer. Then confirm to start by pressing the knob directly at the printer. Now the job starts and you can immediately see it on the Fabman dashboard. When the print is finished, it will be automatically charged according your pricing settings in Fabman.

Installation Guide
------------------

**I'm currently setting up this repository. An installation guide will be provided here soon. Thank you for your patience.**

If you cannot wait any longer, please [contact me](mailto:info@happylab.at) directly.
