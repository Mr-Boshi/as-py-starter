# Function to read dynamics from dyn/*
def dynreader(exp_file):
	with open('exp/'+exp_file, 'r') as f:
		file = f.read().splitlines()

	iterator = 0
	for line in file:
		found = line.find('PRAD')
		iterator +=1
		if not found == -1:
			times=file[iterator].split()
			dyn_duration = float(times[-1])-float(times[0])
		
	return dyn_duration
