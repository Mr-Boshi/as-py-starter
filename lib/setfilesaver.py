# Function to save input arguments into file
def setfilesaver(astrastring, modelvars, anomvars, tm):
	import json
	# Saving input parameters to file
	localtime = tm.localtime(tm.time())
	timndat = str(localtime.tm_year)+'.'+str(localtime.tm_mon)+'.'+str(localtime.tm_mday) + \
			'-'+str(localtime.tm_hour)+':' + \
			str(localtime.tm_min)+':'+str(localtime.tm_sec)
	filename = timndat+' '+astrastring['exp']+' '+astrastring['param']+'.txt'
	print('Input parameters will be saved into file: '+filename)

	# Constructing sh command string

	# Forming save file
	data2save = "=============================================================\n" + \
			"Astra parameters:\n" + \
			json.dumps(astrastring) + '\n' + \
			"=============================================================\n" + \
			'Model parameters:\n' + \
			json.dumps(modelvars) + '\n' + \
			"=============================================================\n" + \
			"Transport variables:\n" + \
			json.dumps(anomvars)

	with open('dat/pylog/'+filename, 'a+') as f:
		f.write(data2save)
