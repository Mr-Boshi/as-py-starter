"""
	! Script to model tungsten removal with ASTRA+STRAHL

	! Required packages:
		* pandas
		* numpy (included in pandas)
		* scipy
		* matplotlib
		* progress
		* psutil
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
import pandas as pd
import matplotlib.pyplot as pt
import time as tm
import json

## Importing self-made packages
from lib.as_processing 		import as_processing
from lib.datfilesaver  		import datfilesaver
from lib.setfilesaver  		import setfilesaver
from lib.suggester     		import suggester
from lib.dynreader     		import dynreader
from lib.astra_calculation	import astra_calculation


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
	arraydata = pd.read_table(dyn_file_name, sep="\s+", header=0).to_numpy()
	radarray  = pd.read_table(rad_file_name, sep="\s+", header=0).to_numpy()

	os.remove(dyn_file_name)
	os.remove(rad_file_name)

	return arraydata, radarray


# Function to plot time evolution
def timeplotter(subplot_settings, time, indices, model_dynamics, experimental_dynamics, plot_rad):
	pt.subplot(subplot_settings[0], subplot_settings[1], subplot_settings[2])

	pt.plot(time[indices[0]:indices[1]], model_dynamics[indices[0]:indices[1]], label='Calculation')
	pt.plot(time[indices[0]:indices[1]], experimental_dynamics[indices[0]:indices[1]], label='Experiment')

	pt.xlabel('time')
	pt.ylabel('P_rad('+str(plot_rad)+')')
	pt.legend()
	pt.grid()


def update_settings(settings_filename, new_cneuts):
	with open(settings_filename, 'r') as f:
		file = f.readlines()

	file[11] = 'initial CNEUT1 (CV4):                 {0}\n'.format(new_cneuts[0])
	file[12] = 'final   CNEUT1 (CV5):                 {0}\n'.format(new_cneuts[1])

	with open(settings_filename, 'w') as f:
		f.writelines(file)
		print('Settings file updated')


#---------------------------------------------------------------------------------------------------------------------------------------
""" Script begins HERE ======================================================================================================================"""
#---------------------------------------------------------------------------------------------------------------------------------------


# Clearing the console and removing results of the prevoius calculation
os.system('clear')
if os.path.isfile('dat/dynam.dat'):
	os.remove('dat/dynam.dat')
if os.path.isfile('dat/radial.dat'):
	os.remove('dat/radial.dat')


# Preallocating needed variables as floats
time = r = prc = pre = pwcalc = pwexp = van = dan = vneo = dneo = nWtot = gradnW = grWvnW = pr_err = float()


# Reading settings
settings_filename = sys.argv[1]
with open(settings_filename, 'r') as f:
	file = f.readlines()
	header_lines = []
	iterator     = 0
	for line in file:
		found = line.find('===')
		iterator += 1
		if not found == -1:
			header_lines.append(iterator)

astrastring        = astra_settings(file, header_lines[1])
modelvars          = model_settings(file, header_lines[2])
transp_sett        = transp_vars(file,    header_lines[3])
execution_settings = exec_settings(file,  header_lines[4])

# Reading dynamics duration from dyn/*
dyndur = dynreader(astrastring.exp, modelvars.dynam_name, float(modelvars.dyn_start))


# Starting astra calculation
dyn_file_name = 'dat/dynam.dat'   # -- where the time evolution is saved
rad_file_name = 'dat/radial.dat'  # -- where the radial profiles are saved

print('\n================================================')
if modelvars.cycle_key:
	iteration = 1                 # -- cycle counter
	print('Autosampling is on')
	while True:
		# Astra calculation
		start_time = tm.time()
		flag       = astra_calculation(astrastring, modelvars, transp_sett,
		                        		dyndur, sys, tm, os)
		
		print('\n================================================\n' +          \
			  'Iteration {0} ended in {1} seconds\n'.format(iteration, round(tm.time()-start_time, 1)))

		if flag:
			# Reading the saved data
			arraydata, radarray = read_astra_results(dyn_file_name, rad_file_name, pd)

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
	start_time = tm.time()
	flag = astra_calculation(astrastring, modelvars, transp_sett,
                        			 dyndur, sys, tm, os)
	print('================================================\n' + \
            'Calculation ended in {0} seconds'.format(round(tm.time()-start_time, 1)))

	if flag:
		# Reading the saved data
		arraydata, radarray = read_astra_results(dyn_file_name, rad_file_name, pd)
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
 gradnW, grWvnW, pr_err, dynamics_indices] = as_processing(arraydata, radarray, dyndur, modelvars)

# print(tungsten_model.density_dynamics[:,1])


#====File saving================================================================
if flag  and execution_settings.saving_settings:
	# Logging used settings
	log_dir = 'dat/pylog'
	make_dir(log_dir)
	setfilesaver(astrastring, modelvars, transp_sett)

if flag and execution_settings.saving_data:
	# Saving results into file
	data_dir        = 'dat/pydat'
	make_dir(data_dir)
	datfilesaver(time, r, tungsten_exp, tungsten_model,
				 anomal_coeffs, nclass_coeffs,
	             gradnW, grWvnW, pr_err,
              astrastring, modelvars)

#====Plotting===================================================================
if flag and execution_settings.plotting_flag:
	fig = pt.figure()  # an empty figure with no axes

	fig.suptitle('W removal')  # Add a title so we know which it is
	radii = [0.00, 2.14, 4.286, 6.428, 8.57, 10.41]
	for i in range(0,6):
		timeplotter([2, 3, i+1], time, dynamics_indices,
		            tungsten_model.density_dynamics[:, i], tungsten_exp.density_dynamics[:, i], radii[i])

#-------------------------------------------------------------------------------

	# fig1 = pt.figure()
	# pt.subplot(1,2,1)
	# pt.plot([0, 3, 6, 9, 12, 15], pr_err)
	# pt.xlabel('r, cm')
	# pt.ylabel('S_0, %')
	# pt.grid()

#-------------------------------------------------------------------------------

	fig2 = pt.figure()
	pt.subplot(2, 3, 3)
	pt.plot(r, tungsten_model.radiation_losses, 'b-', label='Calculation')
	pt.plot(r, tungsten_exp.radiation_losses, 'g-', label='Experiment')
	pt.xlabel('r, cm')
	pt.ylabel('P_rad')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 2)
	pt.plot(r, anomal_coeffs.pinch, 'b-', label='Anomalous')
	pt.plot(r, nclass_coeffs.pinch, 'g-', label='Neoclassic')
	pt.xlabel('r, cm')
	pt.ylabel('V')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 1)
	pt.plot(r, anomal_coeffs.diffusion, 'b-', label='Anomalous')
	pt.plot(r, nclass_coeffs.diffusion, 'g-', label='Neoclassic')
	pt.xlabel('r, cm')
	pt.ylabel('D')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 4)
	pt.plot(r, tungsten_model.total_density)
	pt.xlabel('r, cm')
	pt.ylabel('nW')
	pt.grid()

	pt.subplot(2, 3, 5)
	vvdneo = nclass_coeffs.pinch/nclass_coeffs.diffusion
	vvdneo[0] = 0

	#---------------------------------------------------------------------------
	pt.plot(r, vvdneo, label='vneo/dneo')
	pt.plot(r, grWvnW, label='gradNW/NW')
	pt.xlabel('r, cm')
	pt.ylabel('peaking factors')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 6)
	pt.plot(r, tungsten_exp.radiation_losses/tungsten_model.radiation_losses)
	pt.plot([0, 30], [1, 1], 'k--')
	pt.ylabel('Prad_exp/Prad_calc')
	pt.grid()

	pt.show()
