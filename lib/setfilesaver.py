# Function to save input arguments into file
def setfilesaver(json, dtime, os, astrastring, modelvars, transp_sett, log_dir):
	# Saving input parameters to file
	timndat = dtime.now().strftime('%Y.%m.%d_%H-%M-%S')
	filename = timndat+' '+astrastring.exp+' '+astrastring.param+'.txt'

	# Constructing sh command string

	# Forming save file
	data2save = "=============================================================\n" + \
			"Astra parameters:\n" + \
			json.dumps(astrastring.to_json()) + '\n' + \
			"=============================================================\n" + \
			'Model parameters:\n' + \
			json.dumps(modelvars.to_json()) + '\n' + \
			"=============================================================\n" + \
			"Transport settings:\n" + \
			transp_sett.radii        + '\n' + \
			transp_sett.an_dif       + '\n' + \
			transp_sett.an_pinch     + '\n'

	file_path = os.path.join(log_dir, filename)
	with open(file_path, 'a+') as f:
		f.write(data2save)

	print('Input parameters saved into file: '+file_path)
