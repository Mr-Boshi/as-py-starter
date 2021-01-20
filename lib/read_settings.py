def read_settings(filename):
	"""
	This subroutine reads data from %filename and constructs parameters needed
	to start ASTRA-STRAHL
	"""

	file = open(filename).read().splitlines()

	# Reading astra parameters
	astrastring = dict()
	astrastring['model']    = file[3].split(':')[-1].strip()
	astrastring['exp']      = file[4].split(':')[-1].strip()
	astrastring['param']    = file[5].split(':')[-1].strip()
	astrastring['st_time']  = file[6].split(':')[-1].strip()
	astrastring['end_time'] = file[7].split(':')[-1].strip()

	bakkey = file[8].split(':')[-1].strip()
	if bakkey.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']:
		astrastring['backkey']  = '-b'
	else:
		astrastring['backkey'] = ''

	# Reading model parameters
	modelvars = dict()
	modelvars['init_cneut'] = file[11].split('--')[0].strip()
	modelvars['end_cneut']  = file[12].split('--')[0].strip()
	modelvars['dyn_start']  = file[13].split('--')[0].strip()
	
	# Reading Transport variables
	cf5  = file[16].split('=')[-1].strip()
	cf6  = file[17].split('=')[-1].strip()
	cf7  = file[18].split('=')[-1].strip()
	cf8  = file[19].split('=')[-1].strip()
	cf9  = file[20].split('=')[-1].strip()
	cf10 = file[21].split('=')[-1].strip()
	cf11 = file[22].split('=')[-1].strip()
	cf12 = file[23].split('=')[-1].strip()
	cf13 = file[24].split('=')[-1].strip()
	cf14 = file[25].split('=')[-1].strip()
	cf15 = file[26].split('=')[-1].strip()
	cf16 = file[27].split('=')[-1].strip()

	return astrastring, modelvars, \
		   (cf5, cf6, cf7, cf8, cf9, cf10, cf11, cf12, cf13, cf14, cf15, cf16)
