"""
	! Script to model tungsten removal with ASTRA+STRAHL

	! Required packages:
		* pandas
		* numpy
		* scipy
		* matplotlib
		* progress
		* psutil
	The input parameters are divided in 3 blocks contained in square brackets []
	The example of script execution code:
	python3 start_as.py settings_file

	The Dan and Van in the model are set as follows:
	CAR10 = 1/NE*(RHO/ABC)**2;
	Dan   = CF7*(CF5*CAR10+CF9*exp(-((RHO-CF10)/CF11)**2)+CF12);
	Van   = CF7*(CF6*CAR10*grad(NE)/NE + CF13*exp(-((RHO-CF14)/CF15)**2)+CF16);
"""

#---------------------------------------------------------------------------------------------------------------------------------------

import sys
import os
import pandas as pd
import matplotlib.pyplot as pt
import time as tm

from lib.read_settings import read_settings
from lib.as_processing import as_processing
from lib.matfilesaver  import matfilesaver
from lib.modelsetting  import modelsetting
from lib.setfilesaver  import setfilesaver
from lib.startastra    import startastra
from lib.suggester     import suggester
from lib.dynreader     import dynreader
from lib.strahlcontrol import strahlcontrol


#---------------------------------------------------------------------------------------------------------------------------------------

# Function to cut the [ and ] from the strings
def bracketcutter(arg, key):
	if key == 1:
		arg[-1] = arg[-1][:(-1)]
	else:
		arg[-1] = arg[-1][:(-1)]
		arg[0] = arg[0][1:]

	return arg

#---------------------------------------------------------------------------------------------------------------------------------------

# Function for printing astra parameters to terminal
def cmdprint(astrastring):

	if not astrastring['backkey']:
		key='No'
	else:
		key='Yes'

	print('\n================================================\n')
	print('Astra-Strahl model name: '+astrastring['model'])
	print('Experimental data file:  '+astrastring['exp'])
	print('Strahl param.file:       '+astrastring['param'])
	print('Calculation time:        '+astrastring['st_time'] + ' ... ' + astrastring['end_time'])
	print('Background key:          '+key)
	print('\n================================================\n')

#---------------------------------------------------------------------------------------------------------------------------------------

# Function to plot time evolution
def timeplotter(arg, times):
	pt.subplot(arg[0], arg[1], arg[2])

	pt.plot(time[times[0]:times[1]], prc[times[0]:times[1], arg[3]], label='Calculation')
	pt.plot(time[times[0]:times[1]], pre[times[0]:times[1], arg[3]], label='Experiment')

	pt.xlabel('time')
	pt.ylabel('P_rad('+str(arg[4])+')')
	pt.legend()
	pt.grid()

#---------------------------------------------------------------------------------------------------------------------------------------

# Function start astra


def astra_calculation(astrastring, modelvars, anomvars, dyndur, sys, tm, os):
	# Setting the model file
	modelsetting(astrastring['model'], modelvars, anomvars, dyndur, sys)

	#Printing Astra parameters
	cmdprint(astrastring)
	# Starting Astra calculation.
	# Flag == 1 -- no errors, flag == 0 -- exited with error
	flag = startastra(modelvars, dyndur, anomvars, astrastring, tm, os)
	return flag

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
time = r = prc = pre = pwcalc = pwexp = van = dan = vneo = dneo = nWtot = gradnW = grWvnW = pr_err = 0.

# Reading settings
settings_filename = sys.argv[1]
astrastring, modelvars, anomvars = read_settings(settings_filename)

# Setting shtral.control file
strahlcontrol(astrastring['param'], os)

# Reading dynamics duration from dyn/*
dyndur = dynreader(astrastring['exp'])

# Starting astra calculation

## Flag =     = 1 -- astra finished with no errors, flag = = 0 -- exited with an error
flag       = 0
iteration  = 1 # -- cycle counter
start_time = tm.time()

if modelvars['cyclekey']:
	
	print(print('\n================================================\n'))
	print('Autosampling is on, iteration {0}'.format(iteration))
	
	while True:

		# Astra calculation
		flag = astra_calculation(astrastring, modelvars,
		                         anomvars, dyndur, sys, tm, os)
		print('Calculation ended in {0} seconds'.format(tm.time()-start_time))
		print('\n================================================\n')

		if flag:
			# Reading the saved data, converting it to arrays...
			arraydata = pd.read_table("dat/dynam.dat", sep="\s+", header=0).to_numpy()
			radarray  = pd.read_table("dat/radial.dat", sep="\s+", header=0).to_numpy()

			# ...and removing the files.
			os.remove('dat/dynam.dat')
			os.remove('dat/radial.dat')

			# Calculating CNEUTS for best agreement
			# suggflag == 1 -- good agreement, suggflag == 0 -- need recalculation
			[suggflag, sugg] = suggester(modelvars, arraydata, dyndur)
			if suggflag == 0:
				modelvars['init_cneut'] = str(sugg[0])
				modelvars['end_cneut']  = str(sugg[1])
				iteration =+ 1
				start_time = tm.time()
				print('Starting with new model parameters, iteration {0}'.format(iteration))

			# If agreement is good, process the results of the calculation
			else:
				[time, r, prc, pre, pwcalc, pwexp, van, dan, vneo,
					dneo, nWtot, gradnW, grWvnW, pr_err] = as_processing(arraydata, radarray, dyndur, modelvars)
				break
		else:
			break

else:
	# Astra calculation
	flag = astra_calculation(astrastring, modelvars,
                          anomvars, dyndur, sys, tm, os)
	print('Calculation ended in {0} seconds'.format(tm.time()-start_time))

	if flag:
		# Reading the saved data, converting it to arrays...
		arraydata = pd.read_table("dat/dynam.dat", sep="\s+", header=0).to_numpy()
		radarray  = pd.read_table("dat/radial.dat", sep="\s+",header=0).to_numpy()
		# ...and removing the files.
		os.remove('dat/dynam.dat')
		os.remove('dat/radial.dat')
		
		[time, r, prc, pre, pwcalc, pwexp, van, dan, vneo,
				dneo, nWtot, gradnW, grWvnW, pr_err] = as_processing(arraydata, radarray, dyndur, modelvars)

savingflag   = 1
plottingflag = 0

#====File saving================================================================
if flag == 1 and savingflag == 1:
	# Logging used settings
	setfilesaver(astrastring, modelvars, anomvars, tm)

	# Saving results into .mat-file
	matfilesaver(time, r, prc,
	             pre, pwcalc, pwexp, van, dan, vneo, dneo, nWtot, gradnW, grWvnW, pr_err, tm, \
              	 astrastring, modelvars, anomvars)

#====Plotting===================================================================
if flag == 1 and plottingflag == 1:
	#Getting indecies to cut out dynamics and plots
	timedif1 = abs(time-float(modelvars['end_cneut'])+0.02)
	timedif2 = abs(time-float(modelvars['end_cneut'])-dyndur-0.02)
	times = [timedif1.argsort()[0], timedif2.argsort()[0]]

	fig = pt.figure()  # an empty figure with no axes

	fig.suptitle('W removal')  # Add a title so we know which it is
	timeplotter([2, 3, 1, 0, 0], times)
	timeplotter([2, 3, 2, 1, 0.1], times)
	timeplotter([2, 3, 3, 2, 0.2], times)
	timeplotter([2, 3, 4, 3, 0.3], times)
	timeplotter([2, 3, 5, 4, 0.4], times)
	timeplotter([2, 3, 6, 5, 0.5], times)

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
	pt.plot(r, pwcalc, 'b-', label='Calculation')
	pt.plot(r, pwexp, 'g-', label='Experiment')
	pt.xlabel('r, cm')
	pt.ylabel('P_rad')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 2)
	pt.plot(r, van, 'b-', label='Anomalous')
	pt.plot(r, vneo, 'g-', label='Neoclassic')
	pt.xlabel('r, cm')
	pt.ylabel('V')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 1)
	pt.plot(r, dan, 'b-', label='Anomalous')
	pt.plot(r, dneo, 'g-', label='Neoclassic')
	pt.xlabel('r, cm')
	pt.ylabel('D')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 4)
	pt.plot(r, nWtot)
	pt.xlabel('r, cm')
	pt.ylabel('nW')
	pt.grid()

	pt.subplot(2, 3, 5)
	vvdneo = vneo/dneo
	vvdneo[0] = 0
	#---------------------------------------------------------------------------
	#---------------------------------------------------------------------------
	pt.plot(r, vvdneo, label='vneo/dneo')
	pt.plot(r, grWvnW, label='gradNW/NW')
	pt.xlabel('r, cm')
	pt.ylabel('peaking factors')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 6)
	pt.plot(r, pwexp/pwcalc)
	pt.plot([0, 30], [1, 1], 'k--')
	pt.ylabel('Prad_exp/Prad_calc')
	pt.grid()

	pt.show()
