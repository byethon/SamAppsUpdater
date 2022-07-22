#!/usr/bin/env python

import os
import re
from urllib import request
import requests
import subprocess
import sys
from platform import platform
from multiprocessing import Process,Queue

if (platform()[0:7]=="Windows"):
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

url_format = "https://vas.samsungapps.com/stub/stubDownload.as?appId={}&deviceId={}" \
             "&mcc=425&mnc=01&csc=ILO&sdkVer={}&pd=0&systemId=1608665720954&callerId=com.sec.android.app.samsungapps" \
             "&abiType=64&extuk=0191d6627f38685f"

regex_info = re.compile(r".*<resultMsg>(?P<msg>[^']*)</resultMsg>"
                        r".*<downloadURI><!\[CDATA\[(?P<uri>[^']*)\]\]></downloadURI>"
                        r".*<versionCode>(?P<vs_code>\d+)</versionCode>", re.MULTILINE | re.DOTALL)

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    OKPURPLE = '\033[95m'
    INFOYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
def devproc():
	devproc=subprocess.Popen(["adb","shell","getprop","ro.product.model"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	andproc=subprocess.Popen(["adb","shell","getprop","ro.build.version.sdk"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	andout = andproc.stdout.read()
	andout = andout.decode('utf-8')
	andout = andout.strip()
	devout = devproc.stdout.read()
	devout = devout.decode('utf-8')
	devout = devout.strip()
	return (devout, andout)

(model,sdk_ver)=devproc()
while(model==''):
	(model,sdk_ver)=devproc()
	print(f"{bcolors.FAIL}ERROR : Device not connected or authorization not granted{bcolors.ENDC}")
	print(f"{bcolors.INFOYELLOW}INFO  : Connect the device and grant authorization for USB debugging{bcolors.ENDC}\033[A\033[A")

def modeprint():
	qmode=0
	print("Select mode to use:")
	print("	(1)  :  Quick mode")
	print("	(2)  :  Normal mode(Only enabled apps)")
	print("	(3)  :  All apps Mode")
	print("	(0)  :  Exit")
	mode = input(f"{bcolors.OKBLUE}  Enter the number corresponding to the mode to be used: {bcolors.ENDC}")
	if(mode=='1'):
		(mode,qmode)=qmodeprint(mode)
	elif  mode not in ['2','3']:
		(mode,qmode)=modeprint()
	elif mode=='0':
		sys.exit()
	return (mode,qmode)

def qmodeprint(mode):
	print("Select list to use:")
	print("	(1)  :  Enabled Applist")
	print("	(2)  :  Complete Applist")
	print("	(0)  :  Go back to previous Mode selection")
	qmode = input(f"{bcolors.OKBLUE}Enter the number corresponding to the mode to be used: {bcolors.ENDC}")
	if qmode=='0':
		(mode,qmode)=modeprint()
	elif qmode not in ['1','2']:
		(mode,qmode)=qmodeprint(mode)
	return (mode,qmode)

def genapplist(mode,qmode,file):
	if(mode=='2'):
		adbproc=subprocess.Popen(["adb","shell","pm","list","packages","-e","--show-versioncode"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	if(mode=='3'):
		adbproc=subprocess.Popen(["adb","shell","pm","list","packages","--show-versioncode"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	adbout=adbproc.stdout.readlines()
	max_i=len(adbout)
	i=0
	applist=[]
	while i<max_i:
		adbout[i]=adbout[i].decode('utf-8').rstrip()
		adbout[i]=adbout[i].split(' ')
		if(len(adbout[i][0].split(':')[1].split('.'))>1 and adbout[i][0].split(':')[1].split('.')[1] in ['sec','samsung']):
			applist.append((adbout[i][0].split(':')[1],adbout[i][1].split(':')[1]))
		i+=1
	return applist

def loadanimate(itr):
	j=itr%8
	if(j==0):
		print(f'\033[A{bcolors.OKBLUE}⢿{bcolors.ENDC}')
	elif(j==1):
		print(f'\033[A{bcolors.OKBLUE}⣻{bcolors.ENDC}')
	elif(j==2):
		print(f'\033[A{bcolors.OKBLUE}⣽{bcolors.ENDC}')
	elif(j==3):
		print(f'\033[A{bcolors.OKBLUE}⣾{bcolors.ENDC}')
	elif(j==4):
		print(f'\033[A{bcolors.OKBLUE}⣷{bcolors.ENDC}')
	elif(j==5):
		print(f'\033[A{bcolors.OKBLUE}⣯{bcolors.ENDC}')
	elif(j==6):
		print(f'\033[A{bcolors.OKBLUE}⣟{bcolors.ENDC}')
	elif(j==7):
		print(f'\033[A{bcolors.OKBLUE}⡿{bcolors.ENDC}')

def urlproc(app):
	url = url_format.format(app[0], model.upper(), sdk_ver)
	return requests.get(url).text


def update(app):
	url=urlproc(app)
	match = [m.groupdict() for m in regex_info.finditer(url)]
	if not match:
		error_msg = re.compile(r"resultMsg>(.*)</resultMsg>").findall(url)
		while(error_msg==0):
			urlproc(app)
			error_msg = re.compile(r"resultMsg>(.*)</resultMsg>").findall(url)
		if (error_msg!=0 and error_msg[0] not in ['This request is blocked. Please contact administrator of Galaxy Store server.', 'Application is not approved as stub', "Couldn't find your app which matches requested conditions. Please check distributed conditions of your app like device, country, mcc, mnc, csc, api level", 'Application is not allowed to use stubDownload', 'This call is unnecessary and blocked. Please contact administrator of GalaxyApps server.']):
			print(f'\n\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
			print(f'\033[A{bcolors.FAIL}  Looking for updatable packages... ERROR: {bcolors.INFOYELLOW}"{error_msg[0]}"{bcolors.ENDC}')
			print('\033[A ')
			return
		return
	match = match[0]
	print(f'\n\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
	print(f"\033[A  {bcolors.OKPURPLE}Found %s{bcolors.ENDC}"%(app[0]))
	if(match['vs_code']>app[1]):
		print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
		print(f"  {bcolors.INFOYELLOW}Update Availabe!\n{bcolors.ENDC}")
		print(f"  Version code{bcolors.OKPURPLE}(Server)    : %s{bcolors.ENDC}"%(match['vs_code']))
		print(f"  Version code{bcolors.OKBLUE}(Installed) : %s\n{bcolors.ENDC}"%(app[1]))
		print('\n')
		print(f"{bcolors.OKBLUE}\033[A  Download started!...        {bcolors.ENDC}")
		file = request.urlretrieve(match["uri"], f'{app[0]}.apk')
		print(f"{bcolors.OKBLUE}  APK saved: {bcolors.INFOYELLOW}{os.getcwd()}/{file[0]}{bcolors.ENDC}")
	elif(match['vs_code']==app[1]):
		print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
		print(f"  {bcolors.OKGREEN}Already the latest version\n\n{bcolors.ENDC}")
	else:
		print(f'\033[A{bcolors.OKPURPLE}⣿{bcolors.ENDC}')
		print(f"  {bcolors.INFOYELLOW}Installed version higher than that on server?!!\n{bcolors.ENDC}")
		print(f"  Version code{bcolors.OKPURPLE}(Server)    : %s{bcolors.ENDC}"%(match['vs_code']))
		print(f"  Version code{bcolors.OKBLUE}(Installed) : %s\n{bcolors.ENDC}\n"%(app[1]))
	return 1

def loader(itr_shift,max_itr,itr_freq,applist,queue):
	list=[]
	itr=itr_shift
	while itr<max_itr:
		loadanimate(itr)
		ret=update(applist[itr])
		if ret !=None:
			list.append(applist[itr])
		itr+=itr_freq
	queue.put(list)

def chainloader(freq,max,applist):
	clist=[]
	q1=Queue()
	p=[]
	for k in range(freq):
		p.append(Process(target = loader,args=(k,max-k,freq,applist,q1)))
		p[k].start()
	clist=q1.get()
	for k in range(freq-1):
		clist+=q1.get()
	return clist

def insproc(file):
	insproc=subprocess.Popen(["adb","install","-r",file],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
	return insproc.stdout.readlines()

if __name__ == '__main__':
	print("                                                         ")
	print("                                                                    \033[A\033[A")
	print("\nDevice Model detected: %s"%(model))
	print("Android SDK Version: %s\n"%(sdk_ver))
	(mode,qmode)=modeprint()
	if (mode=='1' and os.path.exists(f".list-{model}-{sdk_ver}-Mode-{int(qmode)+1}") and os.stat(f".list-{model}-{sdk_ver}-Mode-{int(qmode)+1}").st_size != 0):
		print("Reading File...")
		listfile= open(f".list-{model}-{sdk_ver}-Mode-{int(qmode)+1}","r")
	else:
		listfile= open(f".list-{model}-{sdk_ver}-Mode-{int(mode)}","w")
		if(mode==1):
			print(f"List not populated, Fallback to Mode-{int(qmode)+1}")
			mode=(f"{int(qmode)+1}")
	applist=genapplist(mode,qmode,listfile)
	downlist=chainloader(8,len(applist),applist)
	print(downlist)
	for data in downlist:
		listfile.write(f"{data[0]}, {data[1]}\n")
	for data in downlist:
		print(f"\n{bcolors.OKBLUE}Install started for {data[0]}{bcolors.ENDC}")
		continue_msg = input(f"{bcolors.OKBLUE}Do you want to install this version? {bcolors.INFOYELLOW}[Y/n]: ")
		print('\n')
		while continue_msg not in ["Y", "y", "", "N", "n"]:
			continue_msg = input(f"{bcolors.OKBLUE}\033[AInput Error. choose {bcolors.INFOYELLOW}[Y/n]: ")
		else:
			if continue_msg in ("N", "n"):
				print(f"{bcolors.OKBLUE}\033[AOkay, You may try again any time :)\n\n{bcolors.ENDC}")
			if continue_msg in ("Y", "y", ""):
				insout = insproc(data[0])
				while(len(insout)>1 and insout[1]!=b'Success\n'):
					insproc(data[0])
					print(f"{bcolors.FAIL}ERROR : Device not connected or authorization not granted{bcolors.ENDC}")
					print(f"{bcolors.INFOYELLOW}INFO  : Connect the device and grant authorization for USB debugging{bcolors.ENDC}\033[A\033[A")
				print("                                                         ")
				print("                                                                    \033[A\033[A")
				print(f"{bcolors.OKPURPLE}{insout[0].decode('utf-8')}{bcolors.ENDC}{bcolors.OKGREEN}{insout[1].decode('utf-8')}{bcolors.ENDC}")
				print(f"{bcolors.OKPURPLE}Running Post-install Cleanup{bcolors.ENDC}")
				os.remove(data[0])
				print(f"{bcolors.INFOYELLOW}APK Deleted!{bcolors.ENDC}")
				print(f"{bcolors.OKGREEN}DONE!{bcolors.ENDC}\n\n")

	print("\n\t--End of package list--")
	sys.exit("Operation Completed Successfully")