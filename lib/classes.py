class line_process:
	def __init__(self, text, sepatator=':', side=-1):
		self.separator = sepatator
		self.side = side
		self.text = text
		self.str = 'Not defined'

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
		text          = line_process(file)
		self.model    = text.split(line)
		self.exp      = text.split(line+1)
		self.param    = text.split(line+2)
		self.st_time  = text.split(line+3)
		self.end_time = text.split(line+4)
		self.back_key = text.booled(line+5, yes='-b', no='')
		self.cmd_string = '.exe/astra '+' '+self.exp      \
                    				  + ' '+self.model    \
                    				  + ' '+self.st_time  \
                    				  + ' '+self.end_time \
                    				  + ' '+self.back_key

	def to_json(self):
		par_dict = {
					'Model name'   : self.model,
					'Exp. data'    : self.exp,
					'Param.file   ': self.param,
					'End time     ': self.end_time,
					'In background': self.back_key
	        }
		return par_dict

	def cmd(self):
		if self.back_key:
			key = 'Yes'
		else:
			key = 'No'

		cmd_text = '================================================'      + '\n' \
    	         + 'Astra-Strahl model name:         '+self.model   + '\n' \
    	         + 'Experimental data file:          '+self.exp     + '\n' \
    	         + 'Strahl param.file:               '+self.param   + '\n' \
    	         + 'Calculation limits:              '+self.st_time + ' ... ' + self.end_time + '\n' \
    	         + 'Background key:                  '+key                 + '\n' \
    	         + '================================================'
		print(cmd_text)



# Modelling parameters
class model_settings:
	def __init__(self, file, block_line, exp_file):
		text             = line_process(file)
		self.init_cneut  = text.split(block_line)
		self.end_cneut   = text.split(block_line+1)
		self.dyn_start   = text.split(block_line+2)
		self.cycle_key   = text.booled(block_line+3)
		self.sigma_error = float(text.split(block_line+4))
		self.dynam_name  = text.split(block_line+5)
		self.exp         = exp_file
		self.dyndur      = self.get_dyndur()

	def to_json(self):
		par_dict={
		'Initial CNEUT'    : self.init_cneut,
		'Final CNEUT'      : self.end_cneut,
		'Start of dynamics': self.dyn_start
		}
		return par_dict

	def set_new_cneuts(self, new_cneuts):
		self.init_cneut = str(new_cneuts[0])
		self.end_cneut  = str(new_cneuts[1])

	def cmd(self):
		low_cimp4 = [float(self.dyn_start)-0.01,
              float(self.dyn_start)+float(self.dyndur)+0.01]
	
		#Setting a pretty message to terminal
		cmd_text = 'Initial CNEUT1:                  '+str(self.init_cneut) + '\n' \
    	         + 'Final   CNEUT1:                  '+str(self.end_cneut) + '\n' \
    	         + 'Start Dynamics:                  '+str(self.dyn_start) + '\n' \
    	         + 'Dynamics duration:               '+str(self.dyndur) + '\n' \
    	         + 'Detailed calculation:            '+str(low_cimp4[0]) + '...' + str(low_cimp4[1]) + '\n' \
    	         + 'Time of ASTRA termination:       '+str(2*float(self.dyn_start)+float(self.dyndur)+2*0.01) + '\n' \
    	         + '================================================'
		# Printing model parameters
		print(cmd_text)

	def get_dyndur(self):
		from lib.line_finder import line_finder
		# Reading exp-file
		with open('exp/'+self.exp, 'r') as f:
			file = f.readlines()

		# Looking for the first line with $search_key in it
		[iterator, times_line] = line_finder(file, self.dynam_name)

		dyn_start = float(self.dyn_start)
		
		# If line is not found, returning None
		if times_line is None:
			dyn_duration = None

		# If line is found, changing starting time
		else:
			# Saving old time points
			old_start     = float(times_line[0])

			#Allocating vars
			times         = []
			new_time_line = ''

			#Forming list of new time points as old + (new start time - old start time) and concotinate it to string 
			for points in times_line:
				times.append(float(points) - old_start + dyn_start)
				new_time_line += str(times[-1]) + ' '

			# Getting dynamic parocess duration as last time point - start time
			dyn_duration   = round(times[-1] - dyn_start, 3)
			
			# Adding new times line to file data and writing it down into file
			file[iterator] = new_time_line + '\n'
			with open('exp/'+self.exp, 'w') as f:
				f.writelines(file)

		return dyn_duration

# Quality metrics
class metrics:
	def __init__(self):
		self.max = None
		self.min = None
		self.mean = None
		self.sum = None
	def plot(self):
		import matplotlib.pyplot as plot

		fig, axs = plot.subplots(1, 3, sharey=True, tight_layout=True)
		axs[0].bar([1, 2, 3, 4, 5, 6], self.max)
		axs[1].bar([1, 2, 3, 4, 5, 6], self.min)
		axs[2].bar([1, 2, 3, 4, 5, 6], self.mean)

		return axs
		# plot.show()
	
	def set(self, _max, _min, _mean):
		self.max  = _max
		self.min  = _min
		self.mean = _mean



# Other settings
class exec_settings:
	def __init__(self, file, block_line):
		text = line_process(file)
		self.saving_settings = text.booled(block_line)
		self.saving_data     = text.booled(block_line+1)
		self.plotting_flag   = text.booled(block_line+2)
		self.saving_plot     = text.booled(block_line+3)
		self.auto_update     = text.booled(block_line+4)
		self.log_dir         = text.split(block_line+5)
		self.data_dir        = text.split(block_line+6)
		self.plot_dir        = text.split(block_line+7)


class diffusion_coefficients:
	def __init__(self, diffusion, pinch):
		self.diffusion = diffusion
		self.pinch     = pinch

class tungsten_data:
	def __init__(self, radiation_losses, density_dynamics, total_density=None):
		import numpy as np
		self.radiation_losses = radiation_losses
		self.total_density    = total_density
		self.density_dynamics = density_dynamics
		self.grad_nW = np.gradient(self.total_density)
		self.grW_nW = self.grad_nW / self.total_density


# Function to read anomalous transport coefficients
class transp_vars:
	def __init__(self, file, block_line):
		text = line_process(file)
		raw_line = text.split(block_line)
		extras = r'[],{}()'
		for letter in extras:
			raw_line = raw_line.replace(letter, '')
		self.output_radii = raw_line.split(' ')
		self.radii        = text.split(block_line+2)
		self.an_dif       = text.split(block_line+3)
		self.an_pinch     = text.split(block_line+4)
		self.dif_factor   = float(text.split(block_line+5))
		self.pinch_factor = float(text.split(block_line+6))

	def to_json(self):
		par_dict = {
                    'Radial grid'  : self.radii,
                    'An. diffusion': self.an_dif,
                    'An. pinch'    : self.an_dif
		}
		return par_dict

	def factorize(self, parameter):
		'''
		A function to multiply the transport coefficients on the factor from the parameters_file
		Needs to be called with a parameter: pinch or diffusion
		'''
		if parameter == 'pinch':
			line   = self.an_pinch
			factor = self.pinch_factor
		elif parameter == 'diffusion':
			line   = self.an_dif
			factor = self.dif_factor
		else:
			return None
			
		splitted_line      = [inst for inst in line.split(' ')]
		factorised_numbers = [(float(inst) * factor) for inst in splitted_line if inst]
		factorised_str     = ''

		for inst in factorised_numbers:
			factorised_str = factorised_str + str(inst) + ' '

		return factorised_str



# Class to store errors
class errors:
	def __init__(self, arg1, arg2):
		max_ar = max(arg1, arg2)
		min_ar = min(arg1, arg2)
		self.error = max_ar/min_ar
		self.rel_error = self.error - 1

	
