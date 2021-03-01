def startastra(modelvars, dyndur, anomvars, astrastring, tm, os):				# Function to start astra
	from progress.spinner import MoonSpinner
	from lib.processfinder import processfinder

	# Printing model parameters
	cmd_text =    'Initial CNEUT1:                  '+str(modelvars.init_cneut) + '\n' \
            	+ 'Final   CNEUT1:                  '+str(modelvars.end_cneut)  + '\n' \
            	+ 'Start Dynamics:                  '+str(modelvars.dyn_start)  + '\n' \
            	+ 'Duration of detaled calculation: '+str(dyndur)               + '\n' \
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
