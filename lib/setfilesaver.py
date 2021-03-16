# Function to save input arguments into file
def setfilesaver(astrastring, modelvars, transp_sett):
	import json
	from datetime import datetime as dtime
	# Saving input parameters to file
	timndat = dtime.now().strftime('%Y.%m.%d_%H-%M-%S')
	filename = timndat+' '+astrastring.exp+' '+astrastring.param+'.txt'
	print('Input parameters will be saved into file: '+filename)

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

	with open('dat/pylog/'+filename, 'a+') as f:
		f.write(data2save)

