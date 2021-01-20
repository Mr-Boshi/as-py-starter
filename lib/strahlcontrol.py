def strahlcontrol(filename, os):													# Function to set strahl.control file
	# shutil.copy('./strahl.control', './strahl.control_backup')
	os.system('mv ./strahl.control ./strahl.control_backup')

	file = open('strahl.control', 'w+')
	file.write(filename + '\n')
	file.write('   0.0' + '\n')
	file.write('E' + '\n')
	file.close()
