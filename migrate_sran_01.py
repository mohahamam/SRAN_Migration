import re,csv

def find_between(s, start, end):
	  return (s.split(start))[1].split(end)[0]	


######################## Get a dictionary out of the csv file of vlans
def csv_list_of_vlans(listfile):
	with open(listfile,'r',newline='') as a:
		reader = csv.reader(a,delimiter=',')
		outputdict = dict((rows[0],rows[1]) for rows in reader if rows!=[] and not (rows[0].startswith('#')))
		return(outputdict)

listofvlansandqos= csv_list_of_vlans('modules/list_of_vlans.csv')
listofvlans1 = list(listofvlansandqos.keys())



def extract_bridgeports(inputfile,listofvlans):
	with open (inputfile,'r') as configfile:
		bridgeport=''
		vlansconfig=''
		pvids = ''
		correctvlansconfig = ''

		for line in configfile:
			for i in listofvlans.items():
				if re.search(r'configure bridge port [\d\/]* vlan-id '+(i)[0], line):
					bridgeport += str (line)
				elif re.search(r'configure bridge port [\d\/]* pvid '+(i)[0], line):
					pvids += str(line)
				elif str('configure vlan id '+(i)[0]) in line:
					vlansconfig += str(line)
					correctvlansconfig += str('configure vlan id '+ (i)[0]+ ' in-qos-prof-name name:'+ (i)[1]+'\n' )
					
		return (bridgeport,vlansconfig,pvids,correctvlansconfig)	
	

service,vlans,pvidlines,corrctvlans = extract_bridgeports('DXB-ONS-AO01_log.txt', listofvlansandqos)

with open ('workingfile.txt','w') as file1, open('OriginalConfig.txt','w') as file2, open('retriveTcont.txt','w') as file3:					
###############################list of orignal filtered Vlans##############################
	file2.write(('#'*30)+'#list of orignal filtered Vlans'+('#'*30)+'\n'+vlans)
	#print(('#'*30)+'#list of orignal filtered Vlans'+('#'*30)+'\n'+vlans)
	file2.write(('#'*30)+'#list of orignal services'+('#'*30)+'\n'+service)

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
	defaultTCBP=[]
	bridgeportexpression = r'1/1/\d*/\d*/\d*/\d*/\d*'
	for line in servicelines:
		for i in listofvlansandqos.items():
			if (i)[1]=='Ingress_Default':
				if re.search(r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id '+(i)[0], line):
					defaultingressBP +=re.findall(bridgeportexpression, line)
					#print(re.findall(bridgeportexpression, line))
			elif (i)[1]=='Default_TC3':
				if re.search(r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id '+(i)[0], line):
					defaultTCBP +=(re.findall(bridgeportexpression, line))
					#print(re.findall(bridgeportexpression, line))
	defaultingressBP = sorted(set(defaultingressBP))
	defaultTCBP = 	sorted(set(defaultTCBP))
	print(defaultingressBP)
	print(defaultTCBP)
	
	expression2 = r'(configure bridge port (1/1/\d*/\d*/\d*/\d*/\d* ))'
	onts_ckts = re.findall(expression2,deleteonts)
	onts_ckts = sorted(set(onts_ckts))
	print(('#'*30)+'#Retrive T-containers'+('#'*30))
	for i in onts_ckts:
		file3.write('info configure qos interface '+i[1]+'flat | match exact:bandwidth'+'\n')


	file1.write(('#'*30)+'#Correct T-containers'+('#'*30)+'\n')		
	with open('DXB-ONTS-AO01_tcont.txt','r') as tcontsfile:
		f = tcontsfile.read()
		expression5 = r'(configure qos interface 1/1/\d*/\d*/\d*/\d*/\d* upstream-queue [^\n]*)'
		tcontconfig = re.findall(expression5,f)
#	for line1 in tcontconfig:
#		print(line1)
	for line in tcontconfig:
		#print (defaultingressBP)
		if re.findall(r'1/1/\d*/\d*/\d*/\d*/\d*', line)[0] in defaultingressBP:
			for i in range(8):
				#if re.findall(r'1/1/\d*/\d*/\d*/\d*/\d*', line) in defaultingressBP:
				file1.write(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+str(i)+' ')+' bandwidth-sharing uni-sharing priority '+ str(i+1) +'\n')
				print(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+str(i)+' ')+' bandwidth-sharing uni-sharing priority '+ str(i+1))
			
			
##########################Correct Vlans in-qos-prof-name profile ############################
	file1.write(('#'*30)+'#Correction of vlans'+('#'*30)+'\n'+corrctvlans)
	print(('#'*30)+'#Correction of vlans'+('#'*30)+'\n'+corrctvlans)

###############################Create ONTs Bridge ports##############################
	expression3 = r'configure bridge port 1/1/\d*/\d*/\d*/\d*/\d* vlan-id [^\n]*'
	onts_bridgeports_full = re.findall(expression3,service)

	create_bridge_ports =''
	for i in onts_bridgeports_full:
		create_bridge_ports +=  (i+'\n')
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
