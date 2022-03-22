import os
import re
from urllib import request
import requests
import subprocess
import sys

regex_info = re.compile(r".*<resultMsg>(?P<msg>[^']*)</resultMsg>"
                        r".*<downloadURI><!\[CDATA\[(?P<uri>[^']*)\]\]></downloadURI>"
                        r".*<versionCode>(?P<vs_code>\d+)</versionCode>", re.MULTILINE | re.DOTALL)

mode=''

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    OKPURPLE = '\033[95m'
    INFOYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
def devproc():
	global model
	devproc=subprocess.Popen(["adb","shell","getprop","ro.product.model"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	devout = devproc.stdout.read()
	devout = devout.decode('utf-8')
	devout = devout.strip()
	model = devout

def andproc():
	global sdk_ver
	andproc=subprocess.Popen(["adb","shell","getprop","ro.build.version.sdk"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	andout = andproc.stdout.read()
	andout = andout.decode('utf-8')
	andout = andout.strip()
	sdk_ver = andout

def modesel():
	global mode
	print("Select mode to use:")
	print("	(1)  :  Quick mode")
	print("	(2)  :  Normal mode(Only enabled apps)")
	print("	(3)  :  All apps Mode")
	print("	(0)  :  Exit")
	mode = input(f"{bcolors.OKBLUE}Enter the number corresponding to the mode to be used: {bcolors.ENDC}")
	exec()


def  exec():
	qmode=''
	global mode,adbout,listfile
	if(mode=='1'):
		print('\n')
		print("Select list to use:")
		print("	(1)  :  Enabled Applist")
		print("	(2)  :  Complete Applist")
		print("	(0)  :  Go back to previous Mode selection")
		qmode = input(f"{bcolors.OKBLUE}Enter the number corresponding to the mode to be used: {bcolors.ENDC}")
		if(qmode=='1' or qmode=='2'):
			print("\n  Looking for updatable packages...")
			if (os.path.exists(f".list-{model}-{sdk_ver}-Mode-{int(qmode)+1}") and os.stat(f".list-{model}-{sdk_ver}-Mode-{int(qmode)+1}").st_size != 0):
				listfile= open(f".list-{model}-{sdk_ver}-Mode-{int(qmode)+1}","r")
				listfile.seek(0,2)
				listfile.seek(listfile.tell()-1,0)
				if(listfile.read()=='%'):
					listfile.seek(0,0)
					listmode()
					listfile.close()
				else:
					listfile.close()
					print(f"List not populated, Fallback to Mode-{int(qmode)+1}")
					mode=(f"{int(qmode)+1}")
					exec()
			else:
				print(f"List not populated, Fallback to Mode-{int(qmode)+1}")
				mode=(f"{int(qmode)+1}")
				exec()
		elif(qmode=='0'):
			print(f"\n\t{bcolors.FAIL}RETURN:{bcolors.ENDC} Mode selection initiated\n")
			modesel()
		else:
			print(f"\n\t{bcolors.FAIL}RETURN:{bcolors.ENDC} No or Illegal Input detected\n")
			modesel()
	elif(mode=='2'):
		print("\n  Looking for updatable packages...")
		adbproc=subprocess.Popen(["adb","shell","pm","list","packages","-e","--show-versioncode","|","cut","-f2-3","-d:"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
		adbout = adbproc.stdout.readlines()
		listfile=open(f".list-{model}-{sdk_ver}-Mode-2","w")
		directmode()
		listfile.write('%')
		listfile.close()
	elif(mode=='3'):
		print("\n  Looking for updatable packages...")
		adbproc=subprocess.Popen(["adb","shell","pm","list","packages","--show-versioncode","|","cut","-f2-3","-d:"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
		adbout = adbproc.stdout.readlines()
		listfile=open(f".list-{model}-{sdk_ver}-Mode-3","w")
		directmode()
		listfile.write('%')
		listfile.close()
	elif(mode=='0'):
		sys.exit(f"\n\t{bcolors.FAIL}QUIT:{bcolors.ENDC} Program Aborted by User\n")
	else:
		sys.exit(f"\n\t{bcolors.FAIL}QUIT:{bcolors.ENDC} No or Illegal Input detected\n")

def directmode():
	global package_name,versioncode,listfile
	for pkginsinfo in adbout:
		x=pkginsinfo.decode('utf-8')
		x=x.strip()
		x=x.split(' ')
		package_name=x[0]
		y=x[1].split(':')
		versioncode=y[1]
		print(f"\033[A  {bcolors.OKBLUE}Looking for updatable packages...{bcolors.ENDC}")
		loadanimate()
		urlproc()
		update()
		listfile.flush()

def listmode():
	global package_name,versioncode,listfile
	lines = listfile.read()
	lines = lines.split('$')
	lines.pop()
	for line in lines:
		vercheck=subprocess.Popen(["adb","shell","pm","list","packages","--show-versioncode","|","grep","-w",line,"|","cut","-f3","-d:"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
		verinfo = vercheck.stdout.read()
		verinfo = verinfo.decode('utf-8')
		verinfo = verinfo.strip()
		versioncode=verinfo
		package_name=line
		print(f"\033[A  {bcolors.OKBLUE}Looking for updatable packages...{bcolors.ENDC}")
		loadanimate()
		urlproc()
		update()

def loadanimate():
	global i
	if(i==0):
		print(f'\033[A{bcolors.OKBLUE}⢿{bcolors.ENDC}')
	elif(i==1):
		print(f'\033[A{bcolors.OKBLUE}⣻{bcolors.ENDC}')
	elif(i==2):
		print(f'\033[A{bcolors.OKBLUE}⣽{bcolors.ENDC}')
	elif(i==3):
		print(f'\033[A{bcolors.OKBLUE}⣾{bcolors.ENDC}')
	elif(i==4):
		print(f'\033[A{bcolors.OKBLUE}⣷{bcolors.ENDC}')
	elif(i==5):
		print(f'\033[A{bcolors.OKBLUE}⣯{bcolors.ENDC}')
	elif(i==6):
		print(f'\033[A{bcolors.OKBLUE}⣟{bcolors.ENDC}')
	elif(i==7):
		print(f'\033[A{bcolors.OKBLUE}⡿{bcolors.ENDC}')
		i=-1
	i+=1

def insproc():
	global insout
	insproc=subprocess.Popen(["adb","install","-r",file[0]],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	insout = insproc.stdout.readlines()

def update():
	global errorcount,pkgcount,file,listfile
	match = [m.groupdict() for m in regex_info.finditer(url)]
	if not match:
		# Showing error message from samsung servers
		error_msg = re.compile(r"resultMsg>(.*)</resultMsg>").findall(url)
		while(error_msg==0):
			urlproc()
			error_msg = re.compile(r"resultMsg>(.*)</resultMsg>").findall(url)
		if (error_msg[0] !='Application is not approved as stub' and error_msg[0] !="Couldn't find your app which matches requested conditions. Please check distributed conditions of your app like device, country, mcc, mnc, csc, api level" and error_msg[0] !='Application is not allowed to use stubDownload' and error_msg[0] !='This call is unnecessary and blocked. Please contact administrator of GalaxyApps server.'):
			errorcount+=1
			print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
			print(f'\033[A{bcolors.FAIL}  Looking for updatable packages... ERROR(%d): {bcolors.INFOYELLOW}"{error_msg[0]}"{bcolors.ENDC}'%(errorcount))
			print('\033[A ')
			return
		return

	match = match[0]
	pkgcount+=1
	print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
	print(f"\033[A  {bcolors.OKPURPLE}Found(%d) %s{bcolors.ENDC}"%(pkgcount,package_name))
	if(mode=='2' or mode=='3'):
		listfile.write(package_name)
		listfile.write('$')
	if(match['vs_code']>versioncode):
		print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
		print(f"  {bcolors.INFOYELLOW}Update Availabe!\n{bcolors.ENDC}")
		print(f"  Version code{bcolors.OKPURPLE}(Server)    : %s{bcolors.ENDC}"%(match['vs_code']))
		print(f"  Version code{bcolors.OKBLUE}(Installed) : %s\n{bcolors.ENDC}"%(versioncode))
		continue_msg = input(f"{bcolors.OKBLUE}Do you want to install this version? {bcolors.INFOYELLOW}[Y/n]: ")
		print('\n')
		# Download the apk file
		while continue_msg not in ["Y", "y", "", "N", "n"]:
			continue_msg = input(f"{bcolors.OKBLUE}\033[AInput Error. choose {bcolors.INFOYELLOW}[Y/n]: ")
		else:
			if continue_msg in ("N", "n"):
				print(f"{bcolors.OKBLUE}\033[AOkay, You may try again any time :)\n\n{bcolors.ENDC}")
			if continue_msg in ("Y", "y", ""):
				print(f"{bcolors.OKBLUE}\033[ADownload started!...        {bcolors.ENDC}")
				file = request.urlretrieve(match["uri"], f'{package_name}.apk')
				print(f"{bcolors.OKBLUE}APK saved: {bcolors.INFOYELLOW}{os.getcwd()}/{file[0]}{bcolors.ENDC}")
				print(f"\n{bcolors.OKBLUE}Install started!...{bcolors.ENDC}")
				insproc()
				while(insout[1]!=b'Success\n'):
					insproc()
					print(f"{bcolors.FAIL}ERROR : Device not connected or authorization not granted{bcolors.ENDC}")
					print(f"{bcolors.INFOYELLOW}INFO  : Connect the device and grant authorization for USB debugging{bcolors.ENDC}\033[A\033[A")
				print("                                                         ")
				print("                                                                    \033[A\033[A")
				print(f"{bcolors.OKPURPLE}{insout[0].decode('utf-8')}{bcolors.ENDC}{bcolors.OKGREEN}{insout[1].decode('utf-8')}{bcolors.ENDC}")
				print(f"{bcolors.OKPURPLE}Running Post-install Cleanup{bcolors.ENDC}")
				os.remove(file[0])
				print(f"{bcolors.INFOYELLOW}APK Deleted!{bcolors.ENDC}")
				print(f"{bcolors.OKGREEN}DONE!{bcolors.ENDC}\n\n")
	elif(match['vs_code']==versioncode):
		print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
		print(f"  {bcolors.OKGREEN}Already the latest version\n\n{bcolors.ENDC}")
	else:
		print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
		print(f"  {bcolors.INFOYELLOW}Installed version higher than that on server?!!\n{bcolors.ENDC}")
		print(f"  Version code{bcolors.OKPURPLE}(Server)    : %s{bcolors.ENDC}"%(match['vs_code']))
		print(f"  Version code{bcolors.OKBLUE}(Installed) : %s\n{bcolors.ENDC}\n"%(versioncode))

def urlproc():
	global url
	url = url_format.format(package_name, model.upper(), sdk_ver)
	url = requests.get(url).text

# set url format
url_format = "https://vas.samsungapps.com/stub/stubDownload.as?appId={}&deviceId={}" \
             "&mcc=425&mnc=01&csc=ILO&sdkVer={}&pd=0&systemId=1608665720954&callerId=com.sec.android.app.samsungapps" \
             "&abiType=64&extuk=0191d6627f38685f"

i=0
pkgcount=0
errorcount=0
devproc()
while(model==''):
	devproc()
	print(f"{bcolors.FAIL}ERROR : Device not connected or authorization not granted{bcolors.ENDC}")
	print(f"{bcolors.INFOYELLOW}INFO  : Connect the device and grant authorization for USB debugging{bcolors.ENDC}\033[A\033[A")
print("                                                         ")
print("                                                                    \033[A\033[A")
print("\nDevice Model detected: %s"%(model))
andproc()
print("Android SDK Version: %s\n"%(sdk_ver))
modesel()
print("\n\t--End of package list--")
sys.exit("Operation Completed Successfully")





