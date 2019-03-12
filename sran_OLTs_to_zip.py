from zipfile import ZipFile
import os,re,pprint


sourcedir = input('Please Give the source directory name: Default=[outputfiles]:\n')
if sourcedir=="":
	sourcedir = 'outputfiles'

output_zip = input('Please Give a name to the output ZIP file: Defulat=[SRAN_correctionFiles.zip]:\n')
if output_zip.endswith('.zip'):
	pass
elif output_zip=="":
	output_zip = "SRAN_correctionFiles.zip"
else:
	output_zip = output_zip+'.zip'

list_of_OLTs=[]
inputfromuser =''
print('\nPlease Provide the IP addresses of all the OLTs you wish to join in excel.\nEvery OLT IP in one line\nWhen finished type < done > then press enter:')
while inputfromuser !='done':
	inputfromuser = input()
	list_of_OLTs += [inputfromuser]

list_of_OLTs.remove('done')
list_of_OLTs = sorted(set(list_of_OLTs))

print('~'*79+'\n')
print("You have entered "+str(len(list_of_OLTs))+' OLTs')
for i in list_of_OLTs:
	print (i)
	
OLTsfolders = os.listdir(sourcedir)
OLTsexpression = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
Readableexpression = r'^CorrectConfig_\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}_.+.txt$'

OLTsfolders=[x for x in OLTsfolders if re.match(OLTsexpression, x) if x in list_of_OLTs ]
print('\nThe following '+str(len(OLTsfolders))+' OLTs were found inside the directory '+sourcedir+':')
if (len(OLTsfolders))==0:
	print("None of the OLTs you have given is inside the source dirctory\nQuitting !!!!")
	exit()



for i in OLTsfolders:
	print (i)
	
readablefiles = []
for i in OLTsfolders:
	readablefiles+= [os.path.join(sourcedir,i,x) for x in os.listdir(os.path.join(sourcedir, i)) if re.match(Readableexpression,x)]

print('~'*79+'\n'+'Below are the files found and will be Zippend in the Zip file\n')

for i in readablefiles:
	print (i)


with ZipFile(output_zip,'w') as zip: 
	for x in readablefiles:
		zip.write(x)
	
	
print("~"*79+'\n\nThe following Zip file has been created which contains the needed files for <'+str(len(OLTsfolders))+'> OLTs \n'+output_zip)