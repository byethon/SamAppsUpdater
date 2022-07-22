# SamAppsUpdater
Automated implementation of David Lev &amp; Yehuda By's SamsungApkDownloader using ADB to retrieve information from the device and seamlessly update apps.

The program first retrieves the model, android version of the device and the list of all the apps(System or User Installed) and checks with the Samsung servers if there are apks available, it then install the update over to the device using adb.

Quick Mode uses a list file of all the available packages for a given device with specific android version allowed by samsung to be downloaded. This list file is automatically generated in Normal and All apps mode when first run thus reducing time required checking for packages that are not available.

Written for and test on linux-based OSes ONLY!

Requires USB debugging on devices to be enabled and ADB to be install and accessible through terminal.

Pyhton modules: os, re, urllib, requests, subprocess, sys have been implemented in the code.

----Beta.py----
Complete design overhaul. Now with support for Windows Systems as well as 8x(1 per available CPU thread) parallel downloading for much faster update process.
NOTE: Downloads are done in one go. User is not asked for any input. User input to install app is required only when launching adb installer.

All the repo files should be in a single directory in Windows Systems as abb.exe needs to be executed from there.
---------------
