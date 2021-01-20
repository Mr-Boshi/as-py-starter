# Function to read dynamics from dyn/*
def dynreader(arg):
	file = open('exp/dyn/AXUV_'+arg+'.dyn', 'r')
	lines = file.readlines()
	line1 = lines[1].strip(' \n')
	line1 = line1.split(' ')
	dyndur = float(line1[-1])-float(line1[0])+0.01
	return dyndur
