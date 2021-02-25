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


import sys
import os
import pandas as pd
import matplotlib.pyplot as pt
import time as tm

from lib.as_processing import as_processing
from lib.datfilesaver  import datfilesaver
from lib.modelsetting  import modelsetting
from lib.setfilesaver  import setfilesaver
from lib.startastra    import startastra
from lib.suggester     import suggester
from lib.dynreader     import dynreader


#---------------------------------------------------------------------------------------------------------------------------------------

class line_process:
	def __init__(self, text, sepatator=':', side=-1):
		self.separator = sepatator
		self.side      = side
		self.text      = text
		self.str       = 'Not defined'
	
	def split(self, line):
		self.str = self.text[line].split(self.separator)[self.side].strip()
		return self.str


	def booled(self, line, yes=True, no=False):
		self.split(line)
		
		if self.str.strip().lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']:
			return yes
		else:
			return no


# Astra parameters
class astra_settings:
	def __init__(self, file, line):
		text = line_process(file)
		self.model    = text.split(line)
		self.exp      = text.split(line+1)
		self.param    = text.split(line+2)
		self.st_time  = text.split(line+3)
		self.end_time = text.split(line+4)
		self.back_key = text.booled(line+5, yes = '-b', no = '')


# Modelling parameters
class model_settings:
	def __init__(self, file, block_line):
		text = line_process(file)
		self.init_cneut = text.split(block_line)
		self.end_cneut  = text.split(block_line+1)
		self.dyn_start  = text.split(block_line+2)
		self.cycle_key  = text.booled(block_line+3)


# Other settings
class exec_settings:
	def __init__(self, file, block_line):
		text = line_process(file)
		self.saving_settings = text.booled(block_line)
		self.saving_data     = text.booled(block_line+1)
		self.plotting_flag   = text.booled(block_line+2)


# Function to read variables CF...CF16
def transp_vars(file, block_line):
	text = line_process(file, sepatator='=')
	cf = list()
	for i in range(12):
		cf.append(text.split(block_line+i))

	return cf


#---------------------------------------------------------------------------------------------------------------------------------------


# def booler(string_to_bool='', yes=True, no=False):
# 	if string_to_bool.strip().lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']:
# 		return yes
# 	else:
# 		return no


# Function for printing astra parameters to terminal
def cmdprint(astrastring):

	if astrastring.back_key:
		key='Yes'
	else:
		key='No'

	print('================================================\n')
	print('Astra-Strahl model name: '+astrastring.model)
	print('Experimental data file:  '+astrastring.exp)
	print('Strahl param.file:       '+astrastring.param)
	print('Calculation time:        '+astrastring.st_time + ' ... ' + astrastring.end_time)
	print('Background key:          '+key)
	print('\n================================================\n')


# Function to start astra
def astra_calculation(astrastring, modelvars, anomvars, dyndur, sys, tm, os):
	# Setting the model file
	modelsetting(astrastring.model, modelvars, anomvars, dyndur, sys)

	#Printing Astra parameters
	cmdprint(astrastring)

	# Starting Astra calculation.
	# Flag == True -- no errors, flag == False -- exited with error
	flag = startastra(modelvars, dyndur, anomvars, astrastring, tm, os)
	return flag


# Function to set strahl.control file
def strahlcontrol(filename, os):
	os.system('mv ./strahl.control ./strahl.control_backup')

	stral_control = '{0}\n   0.0\nE'.format(filename)

	with open('strahl.control', 'w+') as strahl_file:
		strahl_file.write(stral_control)


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
	file = f.read().splitlines()

astrastring        = astra_settings(file, 3)
modelvars          = model_settings(file, 11)
anomvars           = transp_vars(file, 17)
execution_settings = exec_settings(file, 31)


# Setting shtral.control file
strahlcontrol(astrastring.param, os)


# Reading dynamics duration from dyn/*
dyndur = dynreader(astrastring.exp)


# Starting astra calculation
## Flag =     = True -- astra finished with no errors, flag = False -- exited with an error
flag       = False
iteration  = 1 # -- cycle counter
start_time = tm.time()

if modelvars.cycle_key:
	
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
				modelvars.init_cneut = str(sugg[0])
				modelvars.end_cneut  = str(sugg[1])
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
		print(type(arraydata))
		# ...and removing the files.
		# os.remove('dat/dynam.dat')
		# os.remove('dat/radial.dat')
		
		[time, r, prc, pre, pwcalc, pwexp, van, dan, vneo,
				dneo, nWtot, gradnW, grWvnW, pr_err] = as_processing(arraydata, radarray, dyndur, modelvars)


#====File saving================================================================
if flag  and execution_settings.saving_settings:
	# Logging used settings
	setfilesaver(astrastring, modelvars, anomvars, tm)

if flag and execution_settings.saving_data:
	# Saving results into file
	file_descriptor='txt'
	datfilesaver(file_descriptor, time, r, prc,
	             pre, pwcalc, pwexp, van, dan, vneo, dneo, nWtot, gradnW, grWvnW, pr_err, tm, \
              	 astrastring, modelvars, anomvars)

#====Plotting===================================================================
if flag and execution_settings.plotting_flag:
	#Getting indecies to cut out dynamics and plots
	timedif1 = abs(time-float(modelvars.end_cneut)+0.02)
	timedif2 = abs(time-float(modelvars.end_cneut)-dyndur-0.02)
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
