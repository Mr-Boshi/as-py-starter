def startastra(modelvars, dynamics_duration, anomvars, astrastring, tm, os):				# Function to start astra
	from progress.spinner import MoonSpinner
	from lib.processfinder import processfinder

	low_cimp4=[float(modelvars.dyn_start)-0.01, float(modelvars.dyn_start)+float(dynamics_duration)+0.01]
	
	# Printing model parameters
	cmd_text =    'Initial CNEUT1:                  '+str(modelvars.init_cneut) + '\n' \
            	+ 'Final   CNEUT1:                  '+str(modelvars.end_cneut)  + '\n' \
            	+ 'Start Dynamics:                  '+str(modelvars.dyn_start)  + '\n' \
            	+ 'Dynamics duration:               '+str(dynamics_duration) + '\n' \
            	+ 'Detailed calculation:            '+str(low_cimp4[0]) + '...' + str(low_cimp4[1]) + '\n' \
            	+ 'Time of ASTRA termination:       '+str(2*float(modelvars.dyn_start)+float(dynamics_duration)+2*0.01) + '\n' \
        		+ '================================================'
	print(cmd_text)




	# Constructing sh command string
	start_astra_command = '.exe/astra '+' '+astrastring.exp      \
									   +' '+astrastring.model    \
									   +' '+astrastring.st_time  \
									   +' '+astrastring.end_time \
									   +' '+astrastring.back_key

	# Starting ASTRA
	print('Astra messeges:\n')
	os.system(start_astra_command)

	if astrastring.back_key:
		print('================================================')
		process = astrastring.model + '.exe'
		with MoonSpinner('Astra calculation in progress...  ') as bar:
			while processfinder(process):
				tm.sleep(1)
				bar.next()
	
	if os.path.isfile('dat/dynam.dat'):
		flag = True
	else:
		flag = False

	return flag
