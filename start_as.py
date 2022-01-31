"""
	! Script to model tungsten removal with ASTRA+STRAHL

	! Install required packages by running
	%python_path -m pip install -r %current_dir%/requirements.txt
	For example:
	python -m pip install -r requirements.txt
	python3 -m pip install -r requirements.txt

	The example of script execution code:
	python3 start_as.py settings_file

	The Dan and Van in the model are set as follows:
	CAR10 = 1/NE*(RHO/ABC)**2;
	Dan   = CF7*(CF5*CAR10+CF9*exp(-((RHO-CF10)/CF11)**2)+CF12);
	Van   = CF7*(CF6*CAR10*grad(NE)/NE + CF13*exp(-((RHO-CF14)/CF15)**2)+CF16);
"""

#---------------------------------------------------------------------------------------------------------------------------------------

## Importing 3-d party packages
import sys
import os
import json
import psutil
import pandas as pd
import matplotlib.pyplot as pt
import time as tm
import numpy as np

from datetime import datetime as dtime

## Importing self-made packages
from lib.as_processing 		import as_processing
from lib.datfilesaver  		import datfilesaver
from lib.setfilesaver  		import setfilesaver
from lib.suggester     		import suggester
from lib.dynreader     		import dynreader
from lib.astra_calculation	import astra_calculation
from lib.plotting	        import plotting


## Importing self-made classes
from lib.classes import astra_settings, model_settings, exec_settings, transp_vars

#---------------------------------------------------------------------------------------------------------------------------------------
# Function to check if {dir} exists and create it if it doesn't
def make_dir(dir):
	if not os.path.exists(dir):
		print('Path "{0}" not found and was created'.format(dir))
		os.makedirs(dir)


# Reading the saved data, converting it to arrays and removing the saved files.
def read_astra_results(dyn_file_name, rad_file_name, pd):
	arraydata = pd.read_table(dyn_file_name, sep=r"\s+")
	radarray  = pd.read_table(rad_file_name, sep=r"\s+")

	os.remove(dyn_file_name)
	os.remove(rad_file_name)

	return arraydata.to_numpy(), radarray.to_numpy(), list(radarray.columns.to_numpy())


def update_settings(settings_filename, new_cneuts):
	from lib.dynreader import line_finder

	with open(settings_filename, 'r') as f:
		file = f.readlines()

	search_keys = ['CV4', 'CV5']
	key_lines   = []
	for word in search_keys:
		found_line = line_finder(file, word)[0]
		if not found_line == None:
			key_lines.append(line_finder(file, word)[0] - 1)
		else:
			key_lines.append(None)

	file[key_lines[0]] = 'initial CNEUT1 (CV4):                 {0}\n'.format(new_cneuts[0])
	file[key_lines[1]] = 'final   CNEUT1 (CV5):                 {0}\n'.format(new_cneuts[1])

	with open(settings_filename, 'w') as f:
		f.writelines(file)
		print('Settings file updated')


#---------------------------------------------------------------------------------------------------------------------------------------
""" Script begins HERE =============================================================================================================="""
#---------------------------------------------------------------------------------------------------------------------------------------
# Preallocating needed variables as floats
time = r = gradnW = grWvnW = pr_err = float()


# Files where tostop.f saves the data
dyn_file_name = 'dat/dynam.dat'   # -- the time evolution
rad_file_name = 'dat/radial.dat'  # -- the radial profiles


# Clearing the console and removing results of the prevoius calculation
os.system('clear')
if os.path.isfile(dyn_file_name):
	os.remove(dyn_file_name)
if os.path.isfile(rad_file_name):
	os.remove(rad_file_name)


# Reading arguments
args = sys.argv

# if no arguments -- exit
if len(args) == 1:
	print('Execute with a setting_file as the first parameter')
	exit()
# if first argument is a file -- saving its name to a var
elif os.path.isfile(args[1]):
	settings_filename = args[1]
#if not -- exit
else:
	print('Setting_file was not found')
	exit()

# finding settings blocks headers that start with header_separator
header_separator = '==='
with open(settings_filename, 'r') as f:
	file = f.readlines()
	header_lines = []
	iterator     = 0
	for line in file:
		found = line.find(header_separator)
		iterator += 1
		if not found == -1:
			header_lines.append(iterator)

# header_lines[0] is assumed to be a header of description block and i skipped
astrastring        = astra_settings(file, header_lines[1])
modelvars          = model_settings(file, header_lines[2])
transp_sett        = transp_vars(file,    header_lines[3])
execution_settings = exec_settings(file,  header_lines[4])


# Reading dynamics duration from dyn/*
dyndur = dynreader(astrastring.exp, modelvars.dynam_name, float(modelvars.dyn_start))

# Save current time to estimate pewformance
start_time = dtime.now()

# Starting astra calculation
print('\n================================================')
if modelvars.cycle_key:
	iteration = 1                 # -- cycle counter
	print('Autosampling is on')
	while True:
		# Astra calculation
		start_time = dtime.now()
		flag       = astra_calculation(astrastring, modelvars, transp_sett,
                                 dyndur, tm, os, psutil)
		eval_time = dtime.now() - start_time
		print('\n================================================\n' +          \
                    'Iteration {0} ended in {1} seconds\n'.format(iteration, round(eval_time.seconds, 1)))

		if flag:
			# Reading the saved data
			arraydata, radarray, column_names = read_astra_results(dyn_file_name, rad_file_name, pd)

			# Calculating CNEUTS for best agreement
			# suggflag == True -- good agreement, False -- need recalculation
			[suggflag, sugg] = suggester(modelvars, arraydata, dyndur)
			if not suggflag:
				modelvars.set_new_cneuts(sugg)
				iteration += 1
				print('Starting with new model parameters\n')

			# If agreement is good, exit the loop
			else:
				break
		# If astra exited with an error, exit the programm
		else:
			print('Astra exited with error, closing the program' + '\n' +
                  '================================================')
			exit()

	if execution_settings.auto_update:
		update_settings(settings_filename, [modelvars.init_cneut, modelvars.end_cneut])
	
else:
	print('Autosampling is off')
	# Astra calculation
	flag = astra_calculation(astrastring, modelvars, transp_sett,
                          dyndur, tm, os, psutil)
	eval_time = dtime.now() - start_time
	print('================================================\n' + \
            'Calculation ended in {0} seconds'.format(round(eval_time.seconds, 1)))

	if flag:
		# Reading the saved data
		arraydata, radarray, column_names = read_astra_results(
			dyn_file_name, rad_file_name, pd)
		# If astra exited with an error, exit the programm
	else:
		print( 'Astra exited with error, closing the program' + '\n' + \
			   '================================================')
		exit()
print('================================================\n')
		
# Process the results of the calculation
[time, r,
 tungsten_exp, tungsten_model,
 anomal_coeffs, nclass_coeffs,
 pr_err, dynamics_indices] = as_processing(np, arraydata, radarray, dyndur, modelvars, column_names)


#====File saving================================================================
if flag:
	if execution_settings.saving_settings:
		# Logging used settings
		make_dir(execution_settings.log_dir)
		setfilesaver(json, dtime, os, astrastring, modelvars,
		             transp_sett, execution_settings.log_dir)

	if execution_settings.saving_data:
		# Saving results into file
		make_dir(execution_settings.data_dir)
		datfilesaver(dtime, np, json, os, time, r, tungsten_exp, tungsten_model,
					 anomal_coeffs, nclass_coeffs, pr_err,
	                 astrastring, modelvars, execution_settings.data_dir)

	if execution_settings.saving_plot:
		# Saving plots into file
		make_dir(execution_settings.plot_dir)


	if  execution_settings.plotting_flag:
		# Plotting
		plotting(pt, transp_sett.output_radii, r, time, dynamics_indices, tungsten_model,
		         tungsten_exp, anomal_coeffs, nclass_coeffs)
