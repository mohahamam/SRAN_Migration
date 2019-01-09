import re
def find_between(s, start, end):
	  return (s.split(start))[1].split(end)[0]
with open('DXB-ONTS-AO01_tcont.txt','r') as tcontsfile:
	f = tcontsfile.read()

	expression5 = r'(configure qos interface 1/1/\d*/\d*/\d*/\d*/\d* upstream-queue [^\n]*)'
	tcontconfig = re.findall(expression5,f)
for line1 in tcontconfig:
	print(line1)
	with open ('text.text.txt','w') as file1:
		
		for line in tcontconfig:
			for i in range(8):
				file1.write(line.replace(find_between(line, 'upstream-queue', 'bandwidth-profile'),' '+str(i)+' ')+' bandwidth-sharing uni-sharing priority '+ str(i+1) +'\n')
#	for i in range(8):
#		print(line1.replace(find_between(line1, ' upstream-queue ', ' bandwidth-profile '), str(i)))

