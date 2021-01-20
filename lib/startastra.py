def startastra(modelvars, dyndur, anomvars, astrastring, tm, os):															# Function to start astra
	from progress.spinner import MoonSpinner
	from lib.processfinder import processfinder

	# Printing model parameters
	print('\n================================================\n')
	print('Initial CNEUT1:                  '+str(modelvars['init_cneut']))
	print('Final   CNEUT1:                  '+str(modelvars['end_cneut']))
	print('Start Dynamics:                  '+str(modelvars['dyn_start']))
	print('Duration of detaled calculation: '+str(dyndur))
	print('\n================================================\n')

	# Constructing sh command string
	startastra = '.exe/astra '+' '+astrastring['exp']\
							  +' '+astrastring['model']\
							  +' '+astrastring['st_time']\
							  +' '+astrastring['end_time']\
							  +' '+astrastring['backkey']

	# Starting ASTRA
	os.system(startastra)
	tm.sleep(2)

	process = astrastring['model'] + '.exe'

	print('\n\n================================================\n')
	with MoonSpinner('Astra calculation in progress...  ') as bar:
		while processfinder(process):
			tm.sleep(1)
			bar.next()
		else:
			print('\nAstra execution is done')
			if os.path.isfile('dat/dynam.dat'):
				flag = True
			else:
				print('Astra exited with error')
				flag = False

	print('\n================================================\n')
	return flag
