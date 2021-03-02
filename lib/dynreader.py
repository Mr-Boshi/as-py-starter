# Function to read dynamics from dyn/*
def dynreader(exp_file, search_key, dyn_start):
	# Reading exp-file
	with open('exp/'+exp_file, 'r') as f:
		file = f.readlines()

	# Looking for the first line with $search_key in it
	iterator   = 0
	times_line = 'Not found'

	for line in file:
		found = line.find(search_key)
		iterator +=1
		if not found == -1:
			times_line=file[iterator].split()
			break
	
	# If line is found, changing starting time
	if times_line == 'Not found':
		dyn_duration = 0.0
	else:
		old_start     = float(times_line[0])
		times         = []
		new_time_line = ''
		for points in times_line:
			times.append(float(points) - old_start + dyn_start)
			new_time_line += str(times[-1]) + ' '

		dyn_duration   = round(times[-1] - dyn_start, 3)
		file[iterator] = new_time_line + '\n'
		with open('exp/'+exp_file, 'w') as f:
			f.writelines(file)


	return dyn_duration
