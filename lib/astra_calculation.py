# from asyncio import subprocess
from operator import sub
import psutil, subprocess
from datetime import datetime as dtime

# Function to set strahl.control file
def strahlcontrol(filename):
	import os
	os.system('mv ./strahl.control ./strahl.control_backup')

	stral_control = '{0}\n   0.0\nE'.format(filename)

	with open('strahl.control', 'w+') as strahl_file:
		strahl_file.write(stral_control)


# Function to set up the model
def model_setting(model_name, modelvars, transp_sett):
	from lib.line_finder import line_finder

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
		model_data[key_lines[3]] = line_formatter('CV7 = {};									   ! Duration of detaled calculation', modelvars.dyndur)
	
	with open('equ/' + model_name, 'w') as f:
			f.writelines(model_data)

# Function to set up the exp file
def exp_setting(exp_file, transp_sett):
	from lib.line_finder import line_finder

	# Saving contents of the exp file splitted in lines in a variable
	with open('exp/'+exp_file, 'r') as f:
		exp_data = f.readlines()

	search_keys = ['CAR9', 'CAR10']
	while_key = True
	while while_key:
		coeff_line=[]
		for word in search_keys:
			coeff_line.append(line_finder(exp_data, word)[0])

		if coeff_line[0] == None:
			exp_data.append('!!!!!! Anomalous diffusion (rt) [m2/s] \n')
			exp_data.append('GRIDTYPE  18  POINTS 4 NAMEXP  CAR9   NTIMES 1  FACTOR 1 \n')
			exp_data.append('0.01 \n')
			exp_data.append('1.500 \n')
			exp_data.append('0 0.1 0.2 0.3 \n')
			exp_data.append('1.500 1 0.5 0 \n')

			with open('exp/' + exp_file, 'w') as f:
				f.writelines(exp_data)

		if coeff_line[1] == None:
			exp_data.append('!!!!!! Anomalous pinch (rt) [m/s] \n')
			exp_data.append('GRIDTYPE  18  POINTS 31 NAMEXP  CAR10   NTIMES 1  FACTOR 1 \n')
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

	exp_data[dn_lines[0]-3] = 'GRIDTYPE  18  POINTS {points} NAMEXP  CAR9   NTIMES 1  FACTOR 1'.format(points = points) + '\n'
	exp_data[cn_lines[0]-3] = 'GRIDTYPE  18  POINTS {points} NAMEXP  CAR10   NTIMES 1  FACTOR 1'.format(points = points) + '\n'

	exp_data[dn_lines[0]] = transp_sett.radii + '\n'
	exp_data[cn_lines[0]] = transp_sett.radii + '\n'

	exp_data[dn_lines[1]] = transp_sett.factorize('diffusion') +   '\n'
	exp_data[cn_lines[1]] = transp_sett.factorize('pinch') + '\n'

	with open('exp/' + exp_file, 'w') as f:
		f.writelines(exp_data)


# Function to start astra
def startastra(astrastring, tm, os):
	from progress.spinner import MoonSpinner
	from lib.processfinder import processfinder

	# Starting ASTRA
	print('Astra messeges:\n')
	astra_process = subprocess.Popen(['.exe/astra', astrastring.exp, astrastring.model, astrastring.st_time, astrastring.end_time,  astrastring.back_key], stdout=subprocess.DEVNULL)
	# stdout=subprocess.DEVNULL

	if astrastring.back_key:
		tm.sleep(3)
		print('================================================')
		process = astrastring.model + '.exe'
		with MoonSpinner('Astra calculation in progress...  ') as bar:
			while processfinder(psutil, process):
				tm.sleep(1)
				bar.next()
	else:
		astra_process.wait()

	if os.path.isfile('dat/dynam.dat'):
		flag = True
	else:
		flag = False

	return flag

#-------------------------------------------------------------------------------
""" The main function ======================================================="""
#-------------------------------------------------------------------------------
def astra_calculation(astrastring, modelvars, transp_sett, tm, os):
	# Save current time to estimate pewformance
	start_time = dtime.now()
	
	# Setting shtral.control file
	strahlcontrol(astrastring.param)

	# Setting the model file and the exp file
	model_setting(astrastring.model, modelvars, transp_sett)
	exp_setting(astrastring.exp, transp_sett)

	#Printing Astra parameters and model parameters
	astrastring.cmd()
	modelvars.cmd()

	# Starting Astra calculation.
	flag = startastra(astrastring, tm, os)

	# Show how much time did the calculation take
	eval_time = dtime.now() - start_time
	print('================================================\n' + \
            'Calculation ended in {} seconds'.format(round(eval_time.seconds, 1)))

	return flag
