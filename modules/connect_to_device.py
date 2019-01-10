import netmiko,os,sys,arrow,argparse,time,re
sys.path.insert(0, 'modules')
from inputfromuser import canweproceed
from CleanNetmico import strip_ansi_escape_codes


def send_commands_to_OLT(hostname,Username,Password,commandsfile,Verbose):
	from obtain_sip_config import geting_voip_sip_config
	from obtain_sip_config import  convert_config
	from obtain_sip_config import	reboot_ONTs
	
	outdir =os.path.join('outputfiles',hostname)
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	logsdir =os.path.join(outdir,'logs/')
	if not os.path.exists(logsdir):
		os.makedirs(logsdir)
		

	os.system('cls' if os.name == 'nt' else 'clear')
	netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
	                      netmiko.ssh_exception.NetMikoAuthenticationException)
	logfilename=os.path.join(logsdir,'Templog_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')
	originalconfig= os.path.join(outdir,'OriginalSipConfig_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')
	correctedconfig= os.path.join(outdir,'CorrectSipConfig_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')
	rebootingONTs=os.path.join(outdir,'RebootONTs_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')

	try:
		print('~'*79)
		print('connecting to the device',hostname)
		connection = netmiko.ConnectHandler(ip=hostname,device_type='alcatel_sros',username=Username,password=Password)
		print('connection to ',hostname,'is successful',type(connection))
		
		with open (logfilename,'w') as commandsin:
			commandsin.writelines('~'*79+('\n'))
			commandsin.writelines('#'*3+'Connecting to the Device IP ='+hostname+'#'*3+('\n'))
			commandsout =connection.send_config_from_file(config_file=commandsfile)
			if Verbose =='Yes':
				print(strip_ansi_escape_codes(commandsout))
			commandsin.writelines(strip_ansi_escape_codes(commandsout))
		geting_voip_sip_config(logfilename, originalconfig)
		convert_config(originalconfig, correctedconfig)
		reboot_ONTs(correctedconfig, rebootingONTs)				
		connection.disconnect()

	except netmiko_exceptions as e:
		print('Failed to connect to the hostname', hostname, e)
		print('Next...')
		return hostname

	except OSError as err:
		print('An error in the commands was observed please check your commands ',err)
		print('Next...')
		return hostname
		
	except Exception as e:
		print('An Unexpected error occured ')
		print (e.message, e.args)
		print('Next...')
		return hostname
	

def main():
	send_commands_to_OLT('10.33.72.14','isadmin','ANS#150','commandsfile.txt','Yes')

if __name__=='__main__':
	main()