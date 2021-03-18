def cmd_print(astrastring):
	if astrastring.back_key:
		key = 'Yes'
	else:
		key = 'No'

	cmd_text = '================================================'      + '\n' \
             + 'Astra-Strahl model name:         '+astrastring.model   + '\n' \
             + 'Experimental data file:          '+astrastring.exp     + '\n' \
             + 'Strahl param.file:               '+astrastring.param   + '\n' \
             + 'Calculation limits:              '+astrastring.st_time + ' ... ' + astrastring.end_time + '\n' \
             + 'Background key:                  '+key                 + '\n' \
             + '================================================'

	print(cmd_text)

# Function to set strahl.control file
def strahlcontrol(filename, os):
	os.system('mv ./strahl.control ./strahl.control_backup')

	stral_control = '{0}\n   0.0\nE'.format(filename)

	with open('strahl.control', 'w+') as strahl_file:
		strahl_file.write(stral_control)


# Function to start astra
def startastra(modelvars, dynamics_duration, astrastring, tm, os, psutil, MoonSpinner):
	from lib.processfinder import processfinder

	low_cimp4 = [float(modelvars.dyn_start)-0.01,
              float(modelvars.dyn_start)+float(dynamics_duration)+0.01]

	# Printing model parameters
	cmd_text = 'Initial CNEUT1:                  '+str(modelvars.init_cneut) + '\n' \
             + 'Final   CNEUT1:                  '+str(modelvars.end_cneut) + '\n' \
             + 'Start Dynamics:                  '+str(modelvars.dyn_start) + '\n' \
             + 'Dynamics duration:               '+str(dynamics_duration) + '\n' \
             + 'Detailed calculation:            '+str(low_cimp4[0]) + '...' + str(low_cimp4[1]) + '\n' \
             + 'Time of ASTRA termination:       '+str(2*float(modelvars.dyn_start)+float(dynamics_duration)+2*0.01) + '\n' \
             + '================================================'
	print(cmd_text)

	# Starting ASTRA
	print('Astra messeges:\n')
	os.system(astrastring.cmd_string)

	if astrastring.back_key:
		print('================================================')
		process = astrastring.model + '.exe'
		with MoonSpinner('Astra calculation in progress...  ') as bar:
			while processfinder(psutil, process):
				tm.sleep(1)
				bar.next()

	if os.path.isfile('dat/dynam.dat'):
		flag = True
	else:
		flag = False

	return flag


def astra_calculation(astrastring, modelvars, transp_sett, dyndur, sys, tm, os, psutil, MoonSpinner):
	from lib.modelsetting import modelsetting
	# Setting shtral.control file
	strahlcontrol(astrastring.param, os)

	# Setting the model file
	modelsetting(astrastring.model, astrastring.exp, modelvars, dyndur, transp_sett)

	#Printing Astra parameters
	cmd_print(astrastring)

	# Starting Astra calculation.
	flag = startastra(modelvars, dyndur, astrastring, tm, os, psutil, MoonSpinner)
	return flag
