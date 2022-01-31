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


# Modelling parameters
class model_settings:
	def __init__(self, file, block_line):
		text = line_process(file)
		self.init_cneut  = text.split(block_line)
		self.end_cneut   = text.split(block_line+1)
		self.dyn_start   = text.split(block_line+2)
		self.cycle_key   = text.booled(block_line+3)
		self.sigma_error = float(text.split(block_line+4))
		self.dynam_name  = text.split(block_line+5)

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

	def to_json(self):
		par_dict = {
                    'Radial grid'  : self.radii,
                    'An. diffusion': self.an_dif,
                    'An. pinch'    : self.an_dif
		}
		return par_dict


# Class to store errors
class errors:
	def __init__(self, arg1, arg2):
		max_ar = max(arg1, arg2)
		min_ar = min(arg1, arg2)
		self.error = max_ar/min_ar
		self.rel_error = self.error - 1

	
