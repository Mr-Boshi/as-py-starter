# Function to set strahl.control file
def strahlcontrol(filename):
	import os
	os.system('mv ./strahl.control ./strahl.control_backup')

	stral_control = '{0}\n   0.0\nE'.format(filename)

	with open('strahl.control', 'w+') as strahl_file:
		strahl_file.write(stral_control)


# Function to print astra parameters in terminal
def cmd_print_astra(astrastring):
	
	#Setting a pretty message to terminal
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
	#Printing a pretty message
	print(cmd_text)


# Function to print model parameters in terminal
def cmd_print_parameters(modelvars, dynamics_duration):
	low_cimp4 = [float(modelvars.dyn_start)-0.01,
              float(modelvars.dyn_start)+float(dynamics_duration)+0.01]
	
	#Setting a pretty message to terminal
	cmd_text = 'Initial CNEUT1:                  '+str(modelvars.init_cneut) + '\n' \
             + 'Final   CNEUT1:                  '+str(modelvars.end_cneut) + '\n' \
             + 'Start Dynamics:                  '+str(modelvars.dyn_start) + '\n' \
             + 'Dynamics duration:               '+str(dynamics_duration) + '\n' \
             + 'Detailed calculation:            '+str(low_cimp4[0]) + '...' + str(low_cimp4[1]) + '\n' \
             + 'Time of ASTRA termination:       '+str(2*float(modelvars.dyn_start)+float(dynamics_duration)+2*0.01) + '\n' \
             + '================================================'
	# Printing model parameters
	print(cmd_text)


# Function to set up the model
def model_setting(model_name, modelvars, dyndur, transp_sett):
	from lib.dynreader import line_finder

	def line_formatter(line, var = None):
		if var == None:
			return line + '\n'
		else:
			return line.format(var) + '\n'
	

	# Saving contents of the model file splitted in lines in a variable
	with open('equ/'+model_name, 'r') as f:
		model_data = f.readlines()

	search_keys = ['CV4', 'CV5', 'CV6', 'CV7']
	key_lines = []
	for word in search_keys:
			found_line = line_finder(model_data, word)[0]
			if not found_line == None:
				key_lines.append(line_finder(model_data, word)[0] - 1)
			else:
				key_lines.append(None)
	if not key_lines[0] == None:
		model_data[key_lines[0]] = line_formatter('CV4 = {};													! Initial CNEUT1', modelvars.init_cneut)
	if not key_lines[1] == None:
		model_data[key_lines[1]] = line_formatter('CV5 = {};													! Final   CNEUT1', modelvars.end_cneut)
	if not key_lines[2] == None:
		model_data[key_lines[2]] = line_formatter('CV6 = {};													! Start Dynamics', modelvars.dyn_start)
	if not key_lines[3] == None:		
		model_data[key_lines[3]] = line_formatter('CV7 = {};									   ! Duration of detaled calculation', dyndur)
	
	with open('equ/' + model_name, 'w') as f:
			f.writelines(model_data)

# Function to set up the exp file
def exp_setting(exp_file, transp_sett):
	from lib.dynreader import line_finder

	# Saving contents of the exp file splitted in lines in a variable
	with open('exp/'+exp_file, 'r') as f:
		exp_data = f.readlines()

	search_keys = ['CAR9', 'CAR10']
	while_key = True
	while while_key:
		coeff_line=[]
		for word in search_keys:
			coeff_line.append(line_finder(exp_data, word)[0])

		print(coeff_line)

		if coeff_line[0] == None:
			exp_data.append('!!!!!! Anomalous diffusion (rt) [m2/s] \n')
			exp_data.append('GRIDTYPE  18  POINTS 4 NAMEXP  CAR9   NTIMES 1 \n')
			exp_data.append('0.01 \n')
			exp_data.append('1.500 \n')
			exp_data.append('0 0.1 0.2 0.3 \n')
			exp_data.append('1.500 1 0.5 0 \n')

			with open('exp/' + exp_file, 'w') as f:
				f.writelines(exp_data)

		if coeff_line[1] == None:
			exp_data.append('!!!!!! Anomalous pinch (rt) [m/s] \n')
			exp_data.append('GRIDTYPE  18  POINTS 31 NAMEXP  CAR10   NTIMES 1 \n')
			exp_data.append('0.01 \n')
			exp_data.append('1.500 \n')
			exp_data.append('0 0.1 0.2 0.3 \n')
			exp_data.append('0 0.5 1 1.500 \n')

			with open('exp/' + exp_file, 'w') as f:
				f.writelines(exp_data)

		if not None in coeff_line:
			while_key = False

	dn_lines  = [coeff_line[0]+2, coeff_line[0]+3]
	cn_lines  = [coeff_line[1]+2, coeff_line[1]+3]

	points = len(transp_sett.radii.split())
	if not points == len(transp_sett.an_dif.split()) == len(transp_sett.an_pinch.split()):
		print('Anomalous transport oefficients ar not matching sizes. Exiting the program')
		exit()

	exp_data[dn_lines[0]-3] = 'GRIDTYPE  18  POINTS {} NAMEXP  CAR9   NTIMES 1'.format(points) + '\n'
	exp_data[cn_lines[0]-3] = 'GRIDTYPE  18  POINTS {} NAMEXP  CAR10   NTIMES 1'.format(points) + '\n'

	exp_data[dn_lines[0]] = transp_sett.radii + '\n'
	exp_data[cn_lines[0]] = transp_sett.radii + '\n'

	exp_data[dn_lines[1]] = transp_sett.an_dif +   '\n'
	exp_data[cn_lines[1]] = transp_sett.an_pinch + '\n'

	with open('exp/' + exp_file, 'w') as f:
		f.writelines(exp_data)


# Function to start astra
def startastra(astrastring, tm, os, psutil):
	from lib.processfinder import processfinder
	from progress.spinner import MoonSpinner

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

#-------------------------------------------------------------------------------
""" The main function ======================================================="""
#-------------------------------------------------------------------------------
def astra_calculation(astrastring, modelvars, transp_sett, dyndur, tm, os, psutil):
	# Setting shtral.control file
	strahlcontrol(astrastring.param)

	# Setting the model file and the exp file
	model_setting(astrastring.model, modelvars, dyndur, transp_sett)
	exp_setting(astrastring.exp, transp_sett)

	#Printing Astra parameters and model parameters
	cmd_print_astra(astrastring)
	cmd_print_parameters(modelvars, dyndur)

	# Starting Astra calculation.
	flag = startastra(astrastring, tm, os, psutil)
	return flag
