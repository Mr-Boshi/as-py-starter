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
		self.dynam_name = text.split(block_line+4)


# Other settings
class exec_settings:
	def __init__(self, file, block_line):
		text = line_process(file)
		self.saving_settings = text.booled(block_line)
		self.saving_data     = text.booled(block_line+1)
		self.plotting_flag   = text.booled(block_line+2)

class diffusion_coefficients:
	def __init__(self, d_neo, v_neo, d_anom, v_anom):
		self.d_neo  = d_neo
		self.v_neo  = v_neo
		self.d_anom = d_anom
		self.v_anom = v_anom


# Function to read variables CF...CF16
def transp_vars(file, block_line):
	text = line_process(file, sepatator='=')
	cf = list()
	for i in range(12):
		cf.append(text.split(block_line+i))

	return cf


#---------------------------------------------------------------------------------------------------------------------------------------


# Function for printing astra parameters to terminal
def cmd_print(astrastring):
	if astrastring.back_key:
		key='Yes'
	else:
		key='No'

	cmd_text= '================================================'                               + '\n' \
			+ 'Astra-Strahl model name:         '+astrastring.model                                    + '\n' \
			+ 'Experimental data file:          '+astrastring.exp                                      + '\n' \
			+ 'Strahl param.file:               '+astrastring.param                                    + '\n' \
			+ 'Calculation limits:              '+astrastring.st_time + ' ... ' + astrastring.end_time + '\n' \
			+ 'Background key:                  '+key                                                  + '\n' \
			+ '================================================'

	print(cmd_text)

# Function to set strahl.control file
def strahlcontrol(filename, os):
	os.system('mv ./strahl.control ./strahl.control_backup')

	stral_control = '{0}\n   0.0\nE'.format(filename)

	with open('strahl.control', 'w+') as strahl_file:
		strahl_file.write(stral_control)


# Function to start astra. Returns True when astra exited normally and False if an error occured
def astra_calculation(astrastring, modelvars, anomvars, dyndur, sys, tm, os):
	# Setting shtral.control file
	strahlcontrol(astrastring.param, os)

	# Setting the model file
	modelsetting(astrastring.model, modelvars, anomvars, dyndur, sys)

	#Printing Astra parameters
	cmd_print(astrastring)

	# Starting Astra calculation.
	flag = startastra(modelvars, dyndur, anomvars, astrastring, tm, os)
	return flag


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
anomvars           = transp_vars(file, 18)
execution_settings = exec_settings(file, 32)


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
		flag       = astra_calculation(astrastring, modelvars,
		                        		anomvars, dyndur, sys, tm, os)
		
		print('Iteration {0} ended in {1} seconds'.format(iteration, tm.time()-start_time))

		if flag:
			# Reading the saved data
			arraydata, radarray = read_astra_results(dyn_file_name, rad_file_name, pd)

			# Calculating CNEUTS for best agreement
			# suggflag == 1 -- good agreement, suggflag == 0 -- need recalculation
			[suggflag, sugg] = suggester(modelvars, arraydata, dyndur)
			if suggflag == 0:
				modelvars.init_cneut = str(sugg[0])
				modelvars.end_cneut  = str(sugg[1])
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

else:
	print('Autosampling is off')
	# Astra calculation
	start_time = tm.time()
	flag       = astra_calculation(astrastring, modelvars,
                        			anomvars, dyndur, sys, tm, os)
	print('================================================\n' + \
		  'Calculation ended in {0} seconds'.format(tm.time()-start_time))

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
[time, r, prc, pre, pwcalc, pwexp, van, dan, vneo,
 dneo, nWtot, gradnW, grWvnW, pr_err, dynind] = as_processing(arraydata, radarray, dyndur, modelvars)


#====File saving================================================================
if flag  and execution_settings.saving_settings:
	# Logging used settings
	log_dir = 'dat/pylog'
	make_dir(log_dir)
	setfilesaver(astrastring, modelvars, anomvars, tm)

if flag and execution_settings.saving_data:
	# Saving results into file
	file_descriptor = 'txt'
	data_dir        = 'dat/pydat'
	make_dir(data_dir)
	datfilesaver(file_descriptor, time, r, prc,
	             pre, pwcalc, pwexp, van, dan, vneo, dneo, nWtot, gradnW, grWvnW, pr_err, tm,
              	 astrastring, modelvars, anomvars)

#====Plotting===================================================================
if flag and execution_settings.plotting_flag:
	fig = pt.figure()  # an empty figure with no axes

	fig.suptitle('W removal')  # Add a title so we know which it is
	timeplotter([2, 3, 1, 0, 0],   dynind)
	timeplotter([2, 3, 2, 1, 0.1], dynind)
	timeplotter([2, 3, 3, 2, 0.2], dynind)
	timeplotter([2, 3, 4, 3, 0.3], dynind)
	timeplotter([2, 3, 5, 4, 0.4], dynind)
	timeplotter([2, 3, 6, 5, 0.5], dynind)

#-------------------------------------------------------------------------------

	fig1 = pt.figure()
	pt.subplot(1,2,1)
	pt.plot([0, 3, 6, 9, 12, 15], pr_err)
	pt.xlabel('r, cm')
	pt.ylabel('S_0, %')
	pt.grid()

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
