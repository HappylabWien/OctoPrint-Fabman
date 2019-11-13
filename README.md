# OctoPrint-Fabman
<!-- #######  YAY, I AM THE SOURCE EDITOR! #########-->
<h1><span style="font-weight: 400;">Introduction</span></h1>
<p><span style="font-weight: 400;">I'd like to share my experiments with connecting </span><a href="https://octoprint.org/"><span style="font-weight: 400;">OctoPrint</span></a><span style="font-weight: 400;"> to </span><a href="https://fabman.io"><span style="font-weight: 400;">Fabman</span></a><span style="font-weight: 400;"> without the need for a Fabman bridge. </span><strong>The implementation is in a very early stage and not yet tested a lot.</strong></p>
<p><span style="font-weight: 400;">To implement this you need:</span></p>
<ul>
<li style="font-weight: 400;"><span style="font-weight: 400;">Prusa MK3 printer</span></li>
<li style="font-weight: 400;"><span style="font-weight: 400;">Raspberry PI 3</span></li>
<li style="font-weight: 400;"><span style="font-weight: 400;">Micro SD card (min. 8GB)</span></li>
<li style="font-weight: 400;"><span style="font-weight: 400;">Fabman Account (you can get your free trial account </span><a href="https://fabman.io"><span style="font-weight: 400;">here</span></a><span style="font-weight: 400;">)</span></li>
<li style="font-weight: 400;"><span style="font-weight: 400;">WiFi and Internet connection</span></li>
</ul>
<h2><span style="font-weight: 400;">What is Fabman?</span></h2>
<p><span style="font-weight: 400;"></span><a href="https://fabman.io"><span style="font-weight: 400;">Fabman</span></a><span style="font-weight: 400;"> is an all-in-one makerspace management solution. It is the "operating system" for makerspaces, fab labs, coworking spaces or school workshops. It helps to manage machines and members easily, safely & efficiently.</span></p>
<h2><span style="font-weight: 400;">Why OctoPrint?</span></h2>
<p><span style="font-weight: 400;">OctoPrint is a very powerful web-based tool to manage 3d printers. It's 100% open source and supports a </span><a href="https://github.com/foosel/OctoPrint/wiki/Supported-Printers"><span style="font-weight: 400;">wide range of 3d printers</span></a><span style="font-weight: 400;"> - including Prusa, RepRap, Ultimaker, etc. So, if we support Octoprint, we immediately support all of them.</span></p>
<h2><span style="font-weight: 400;">Why connect 3D printers to Fabman?</span></h2>
<p><span style="font-weight: 400;">The main features and advantages of this configuration are:</span></p>
<ul>
<li style="font-weight: 400;"><span style="font-weight: 400;">Permission management: You can control via Fabman who is allowed to print</span></li>
<li style="font-weight: 400;"><span style="font-weight: 400;">Logging: You see all your printing activities at one sight in the Fabman dashboard</span></li>
<li style="font-weight: 400;"><span style="font-weight: 400;">Billing: You can automatically charge according to actual usage of the printer. Time and filament based charges are supported.</span></li>
</ul>
<h2><span style="font-weight: 400;">How to use the OctoPrint with Fabman?</span></h2>
<p><span style="font-weight: 400;">In our approach you simply login to your OctoPrint installation with the login data you use for the Fabman member portal. Thanks to our colleagues at Fab Lab Brno! They published a </span><a href="https://github.com/rplnt/octoprint-fabman-auth"><span style="font-weight: 400;">Plugin f&uuml;r OctoPrint authentication against Fabman</span></a><span style="font-weight: 400;">. We've used it for this part.</span></p>
<p><span style="font-weight: 400;">You can then upload your 3d print file (GCODE file) and send it to the printer. Then confirm to start by pressing the knob directly at the printer. Now the job starts and you can immediately see it on the Fabman dashboard. When the print is finished, it will be automatically charged according your pricing settings in Fabman.</span></p>
<h1><span style="font-weight: 400;">Installation Guide</span></h1>
<p><strong>I'm currently setting up this repository. An installation guide will be provided here soon. Thank you for your patience.&nbsp;</strong></p>
<p><span style="font-weight: 400;">If you cannot wait any longer, please contact me directly.</span></p>
