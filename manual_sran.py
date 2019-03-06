import re,csv,netmiko,os,sys,arrow,argparse,time
sys.path.insert(0, 'modules')
from inputfromuser import canweproceed
from CleanNetmico import strip_ansi_escape_codes

#####################
#def canweproceed():
#	answer = input('Are the above inputs correct? (Yes,No):')
#
#	if answer.lower()=='yes':
#		print('Proceeding to Next Steps....')
#		time.sleep(0.5)
#		pass
#	elif answer.lower()=='y':
#		print('Proceeding to Next Steps....')
#		time.sleep(0.5)
#		pass
#	else:
#		print('You have chosen ',answer)
#		print('Quitting...')
#		time.sleep(0.25)
#		exit()
############################
#
#
#parser = argparse.ArgumentParser(description='''
#This script will provide us commands to correct the SRAN configuration''' )
#parser.add_argument("-ip", help="Mandatory Provide the Host IP address")
#parser.add_argument("-u", help="Mandatory Username of the NE")
#parser.add_argument("-password", help="Mandatory password of the NE")
#	
#args = parser.parse_args()
#hostname=(args.ip)
#username=(args.u)
#password=(args.password)
#
#
#os.system('cls' if os.name == 'nt' else 'clear')
#
####Check the inputs form the user are all correct and prompt him to continue if all OK
#mandatories ={'NE IP':hostname,'NE Username':username,'NE Password':password}
#
#print('List of inputs')
#print('~'*79)
#for key,val in mandatories.items():
#	print (key+' = ',val)
#	if val is None:
#		print('!!!!!!!Erorr\nThe',key,'value should not be empty please re-enter the command with correct inputs for help use -h or --help')
#		print('Quitting....')
#		time.sleep(1)
#		exit()
#		
#print('~'*79)
#canweproceed()
#print('~'*79)
#
#
#
hostname = input('Please Provide the OLT IP Address\n')
#username = input('Please Provide the OLT username\n')
#password = input('Please provide the OLT password\n')

#####################Useful Functions used inside the script###############################
def find_between(s, start, end):
	  return (s.split(start))[1].split(end)[0]	


######################## Get a dictionary out of the csv file of vlans####################
def csv_list_of_vlans(listfile):
	with open(listfile,'r',newline='') as a:
		reader = csv.reader(a,delimiter=',')
		outputdict = dict((rows[0],rows[1]) for rows in reader if rows!=[] and not (rows[0].startswith('#')))
		return(outputdict)

listofvlansandqos= csv_list_of_vlans('modules/list_of_vlans.csv')
listofvlans1 = list(listofvlansandqos.keys())

#######################process the output of the OLT commands

def extract_bridgeports(inputfile,listofvlans):
	with open (inputfile,'r') as configfile:
		bridgeport=''
		vlansconfig=''
		pvids = ''
		correctvlansconfig = ''
		ethline = ''
		for line in configfile:
			if re.search(r'configure ethernet line 1/1/\d+/\d*[13579] port-type', line):
				ethline +=str(line)
			for i in listofvlans.items():
				if re.search(r'configure bridge port [\d\/]* vlan-id '+(i)[0], line):
					bridgeport += str (line)
				elif re.search(r'configure bridge port [\d\/]* pvid '+(i)[0], line):
					pvids += str(line)
				elif str('configure vlan id '+(i)[0]+' mode residential-bridge ') in line:
					vlansconfig += str(line)
					correctvlansconfig += str('configure vlan id '+ (i)[0]+ ' in-qos-prof-name name:'+ (i)[1]+'\n' )		
		return (bridgeport,vlansconfig,pvids,correctvlansconfig,ethline)	
		

############################Main files and directories used in the script#####################
outdir =os.path.join('outputfiles',hostname)
if not os.path.exists(outdir):
	os.makedirs(outdir)

logsdir =os.path.join(outdir,'logs/')
if not os.path.exists(logsdir):
	os.makedirs(logsdir)
#logfilename=input('Please provide the name of input file')
logfilename='LogFile_10.234.228.132_2019-03-05-13-22-23.txt'
#logfilename=os.path.join(logsdir,'LogFile_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')
originalconfig= os.path.join(outdir,'OriginalConfig_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')
correctedconfig= os.path.join(outdir,'CorrectConfig_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')

infoconfqosinterface=os.path.join(logsdir,'infoconfigqos_'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')
#qosinterface=input('please provide qos interface info\n')
qosinterface='infoconfigqos_10.234.228.132_2019-03-05-13-22-23.txt'
#qosinterface=os.path.join(logsdir,'qos_interface_info'+hostname+'_'+ arrow.now().format('YYYY-MM-DD-HH-mm-ss')+'.txt')

commandsfile =os.path.join('modules','list_of_commands.txt')
Verbose ='No'

###################### Running the connection to the OLT
#os.system('cls' if os.name == 'nt' else 'clear')
#netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
#	                      netmiko.ssh_exception.NetMikoAuthenticationException)

try:
#	print('~'*79)
#	print('connecting to the device',hostname)
#	connection = netmiko.ConnectHandler(ip=hostname,device_type='alcatel_sros',username=username,password=password,session_timeout=7200,timeout=7200)
#	print('connection to ',hostname,'is successful',type(connection))
#	
#	with open (logfilename,'w') as commandsin:
#		commandsin.writelines('~'*79+('\n'))
#		commandsin.writelines('#'*3+'Connecting to the Device IP ='+hostname+'#'*3+('\n'))
#		commandsout =connection.send_config_from_file(config_file=commandsfile)
#		if Verbose =='Yes':
#			print(strip_ansi_escape_codes(commandsout))
#		commandsin.writelines(strip_ansi_escape_codes(commandsout))

	############################ Run the function to collect the needed info.

	service,vlans,pvidlines,corrctvlans,ethernetline = extract_bridgeports(logfilename, listofvlansandqos)
	with open(logfilename,'r') as f:
		allconfig=f.read()

	############################Run the main script and save the output to the Files##############
	#file1 will be having the working file commands that you need to execute
	#file2 will be having the Original configuration of the vlans and ONTs
	#file3 will be a file that is used as input to collect QOS T-containers used in ONTs.


	with open (correctedconfig,'w') as file1, open(originalconfig,'w') as file2, open(infoconfqosinterface,'w') as file3:					
	###############################list of orignal filtered Vlans#################################
	
		file2.write(('#'*30)+'#list of orignal filtered Vlans'+('#'*30)+'\n'+vlans)
		file2.write(('#'*30)+'#list of orignal services'+('#'*30)+'\n'+service)
		file2.write(('#'*30)+'#list of pvids'+('#'*30)+'\n'+pvidlines)
		file2.write(('#'*30)+'#list of Ethernetlines '+('#'*30)+'\n'+ethernetline)
	###############################Delete ONTs pvids##############################
		expression0 = r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* pvid'
		onts_bridgeports = re.findall(expression0,pvidlines)
		deletepvids =''
		for i in onts_bridgeports:
			deletepvids +=  (i.replace(' pvid', ' no pvid')+'\n')
		file1.write(('#'*30)+'#Delete ONTs pvids'+('#'*30)+'\n'+deletepvids)
		print(('#'*30)+'#Delete ONTs pvids'+('#'*30)+'\n'+deletepvids)

	###############################Delete ONTs Bridge ports##############################
		expression1 = r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id \w*'
		onts_bridgeports = re.findall(expression1,service)
		deleteonts =''
		for i in onts_bridgeports:
			deleteonts +=  (i.replace(' vlan-id ', ' no vlan-id ')+'\n')
		
		file1.write(('#'*30)+'#Delete ONTs Bridge ports'+('#'*30)+'\n'+deleteonts)	
		print(('#'*30)+'#Delete ONTs Bridge ports'+('#'*30)+'\n'+deleteonts)
	###############################Correct T-containers ##############################
		servicelines =service.split('\n')
		defaultingressBP=[]
		defaultTC3BP=[]
		bridgeportexpression = r'1/1/\d*/\d*/\d*/\d*/\d*'
		for line in servicelines:
			for i in listofvlansandqos.items():
				if (i)[1]=='Ingress_Default':
					if re.search(r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id '+(i)[0], line):
						defaultingressBP +=re.findall(bridgeportexpression, line)
						#print(re.findall(bridgeportexpression, line))
				elif (i)[1]=='Default_TC3':
					if re.search(r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id '+(i)[0], line):
						defaultTC3BP +=(re.findall(bridgeportexpression, line))
						#print(re.findall(bridgeportexpression, line))
		
		
		defaultingressBP = sorted(set(defaultingressBP))
		defaultTC3BP = 	sorted(set(defaultTC3BP))
		
		expression2 = r'(configure bridge port (1/1/\d*/\d*/\d*/\d*/\d* ))'
		onts_ckts = re.findall(expression2,deleteonts)
		onts_ckts = sorted(set(onts_ckts))
		print(('#'*30)+'#Correct T-containers'+('#'*30))
		for i in onts_ckts:
			file3.write('info configure qos interface '+i[1]+'flat | match exact:bandwidth'+'\n')
		file3.close()
		

		
		with open(qosinterface,'r') as tcontsfile:
			f = tcontsfile.read()
			expression5 = r'(configure qos interface 1/1/\d*/\d*/\d*/\d*/\d* upstream-queue [^\n]*)'
			tcontconfig = re.findall(expression5,f)
		file1.close()
		with open (correctedconfig,'a') as file1:
			queues_dic={0:'1',
						1:'1',
						2:'10',
						3:'10',
						4:'50',
						5:'50',
						6:'100',
						7:'127'}	
			file1.write(('#'*30)+'#Correct T-containers'+('#'*30)+'\n')
			for line in tcontconfig:
				if re.findall(r'1/1/\d*/\d*/\d*/\d*/\d*', line)[0] in defaultingressBP:
					for i in range(8):
						#if re.findall(r'1/1/\d*/\d*/\d*/\d*/\d*', line) in defaultingressBP:
						file1.write(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+str(i)+' ')+' bandwidth-sharing uni-sharing priority 1 weight '+ str(queues_dic[i]) +'\n')
						print(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+str(i)+' ')+' bandwidth-sharing uni-sharing priority 1 weight '+ str(queues_dic[i]))
				elif re.findall(r'1/1/\d*/\d*/\d*/\d*/\d*', line)[0] in defaultTC3BP:
					file1.write(re.sub(r'bandwidth-profile name:[^\n]*','bandwidth-profile none',line)+'\n')
					print(re.sub(r'bandwidth-profile name:[^\n]*','bandwidth-profile none',line))
					file1.write(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+'3'+' ')+'\n')
					print(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+'3'+' '))
		####new######################Correct Ethernet Lines form uni to nni#############################
			serviceetherlines = service.split('\n')

			etherlineslist=[]
			for i in serviceetherlines:
				etherlineslist+=(re.findall(r' 1/1/\d+/\d*[13579] ', i))
			etherlineslist = sorted(set(etherlineslist))
		
			#print(etherlineslist)

			ethernetline1 = ethernetline.split('\n')
			ethernetline1 = list(ethernetline1)
			ethernetline1.remove('')
			unietherline = ''
			for line in ethernetline1:
				#print(re.findall(r' 1/1/\d+/\d*[13579] ', line))
				if re.findall(r' 1/1/\d+/\d*[13579] ', line)[0] in etherlineslist:
					if ' port-type uni' in line:
						unietherline+=line+('\n')
			
			unietherline=unietherline.replace('uni','nni')

			print(('#'*30)+'#Correct EthernetLines from uni to nni'+('#'*30)+'\n'+unietherline)
			file1.write(('#'*30)+'#Correct EthernetLines from uni to nni'+('#'*30)+'\n'+unietherline)
		##########################Correct Vlans in-qos-prof-name profile ############################
			file1.write(('#'*30)+'#Correction of vlans'+('#'*30)+'\n'+corrctvlans)
			print(('#'*30)+'#Correction of vlans'+('#'*30)+'\n'+corrctvlans)

		###############################Create ONTs Bridge ports##############################
			expression6=r' qos\spriority:[0-7]'
			expression7=r' in-qos-prof-name\sname:\S+'
			
			expression3 = r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id [^\n]*'
			onts_bridgeports_full = re.findall(expression3,service)

			create_bridge_ports =''
			for i in onts_bridgeports_full:
				create_bridge_ports +=  (re.sub(expression7,"",re.sub(expression6,"" ,i))+'\n')
			file1.write(('#'*30)+'#Create ONTs Bridge ports'+('#'*30)+'\n'+create_bridge_ports)
			print(('#'*30)+'#Create ONTs Bridge ports'+('#'*30)+'\n'+create_bridge_ports)

		###############################Create ONTs pvids##############################
			expression4 = r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* pvid [^\n]*'
			create_pvids = re.findall(expression4,pvidlines)
			createpvid =''
			for i in create_pvids:
				createpvid +=  (i+'\n')
			file1.write(('#'*30)+'#Create ONTs pvids'+('#'*30)+'\n'+createpvid)
			print(('#'*30)+'#Create ONTs pvids'+('#'*30)+'\n'+createpvid)
			

		##########################Handling the AE ports (UNI) to (NNI)



			
			unietherline = unietherline.split('\n')
			unietherline.remove('')#

			listofunilines = []

			for i in unietherline:
				listofunilines+=(re.findall(r' 1/1/\d+/\d*[13579] ', i))
			listofunilines= sorted(set(listofunilines))
			#print(listofunilines)
				
#			ethernetbp = sorted(set(serviceetherlines))
#			ethernetbp.remove('')
#			recreateethlines=''
#			for line in ethernetbp:
#				if re.findall(r' 1/1/\d+/\d*[13579] ', line)!=[]:
#					if re.findall(r' 1/1/\d+/\d*[13579] ', line)[0] in listofunilines:
#						recreateethlines+=line+('\n')
			print (('#'*30)+'#Recreate the Ethernet bridge ports again'+('#'*30))
			file1.write(('#'*30)+'#Recreate the Ethernet bridge ports again'+('#'*30)+'\n')
			for i in allconfig.split('\n'):
				if re.findall(r'configure bridge port(\s1/1/\d+/\d*[13579]\s)',i)!=[]:
					if re.findall(r'configure bridge port(\s1/1/\d+/\d*[13579]\s)',i)[0] in listofunilines:
						print(i)
						file1.write(i+'\n')
	
			
	############################
			
			ethpvids = pvidlines.split('\n')
			ethpvids = list(ethpvids)
			ethpvids.remove('')
			createethpvids = ''
			for line in ethpvids:
				if re.findall(r' 1/1/\d+/\d*[13579] ', line)!=[]:
					if re.findall(r' 1/1/\d+/\d*[13579] ', line)[0] in listofunilines:
						createethpvids+=line

			print(('#'*30)+'#Recreate the Ethernet lines pvid'+('#'*30)+'\n'+createethpvids)
			file1.write(('#'*30)+'#Recreate the Ethernet lines pvid'+('#'*30)+'\n'+createethpvids)
			
#	
#	connection.disconnect()
#	print('~'*30+'\n')
#	print('A file with needed configuration correction has been created under the directory ',outdir+'\n')
#	print('The file name is :',correctedconfig+'\n')
#except netmiko_exceptions as e:
#	print('Failed to connect to the hostname', hostname, e)
#	print('Next...')
#
#
#except OSError as err:
#	print('An error in the commands was observed please check your commands ',err)
#	print('Next...')

	
except Exception as e:
	print('An Unexpected error occured ')
	print (e.message, e.args)
	print('Next...')

	