def datfilesaver(time, r, tungsten_exp, tungsten_model,
				 anomal_coeffs, nclass_coeffs,
				 gradnW, grWvnW, pr_err,
                 astrastring, modelvars):
	from scipy.io import savemat
	from datetime import datetime as dtime
	import numpy as np
	import json

	# Setting savefile name
	timndat = dtime.now().strftime('%Y.%m.%d_%H-%M-%S')
	filename = 'dat/pydat/'+ timndat+' '+astrastring.exp+' '+astrastring.model + '.txt'

	# Forming list of coefficients and model parameters
	modl = [float(modelvars.init_cneut), float(modelvars.end_cneut), float(modelvars.dyn_start), float(modelvars.cycle_key)]

	with open(filename, 'w') as f:
		time_points   = time.size
		radial_points = r.size
		data_format   = '%11.4E'

	# Radius (in cm)
		np.savetxt(f, r.reshape((-1, radial_points)), fmt=data_format,
				   header='Radius (in cm):', footer='#')
	# Radial profiles of Prad
		np.savetxt(f, tungsten_model.radiation_losses.reshape((-1, radial_points)), fmt=data_format,
				   header='Calculated radial profile of Prad:', footer='#')
		np.savetxt(f, tungsten_exp.radiation_losses.reshape((-1, radial_points)), fmt=data_format,
				   header='Experimental radial profile of Prad:', footer='#')
	# Anomalous coefficients
		np.savetxt(f, anomal_coeffs.diffusion.reshape((-1, radial_points)),
				   fmt=data_format, header='Anomalous diffusion:', footer='#')
		np.savetxt(f, anomal_coeffs.pinch.reshape((-1, radial_points)),
				   fmt=data_format, header='Anomalous pinch:', footer='#')
	# Neoclassic coefficients
		np.savetxt(f, nclass_coeffs.diffusion.reshape((-1, radial_points)),
				   fmt=data_format, header='Neoclassic diffusion:', footer='#')
		np.savetxt(f, nclass_coeffs.pinch.reshape((-1, radial_points)),
				   fmt=data_format, header='Neoclassic pinch:', footer='#')
	# W density profile
		np.savetxt(f, tungsten_model.total_density.reshape((-1, radial_points)),
				   fmt=data_format, header='Total impurity density:', footer='#')

		np.savetxt(f, gradnW.reshape((-1,radial_points)), fmt=data_format, header='gradnW:', footer='#')
		np.savetxt(f, grWvnW.reshape((-1,radial_points)), fmt=data_format, header='grW/vnW:', footer='#')

		f.write('\n')

	# Times
		np.savetxt(f, time.reshape((1,time_points)), fmt=data_format, header='Times:', footer='#')
	# Time evolution of Prad
		prc_shaped = tungsten_model.density_dynamics.reshape((time_points, -1))
		np.savetxt(f, prc_shaped.transpose(), fmt=data_format,
				   header='Calculated time evolution of Prad:', footer='#')
		pre_shaped = tungsten_exp.density_dynamics.reshape((time_points, -1))
		np.savetxt(f, pre_shaped.transpose(), fmt=data_format,
				   header='Experimental time evolution of Prad:', footer='#')

		f.write('\n')

		f.write('# Calculation settings\n')			
		data2save = json.dumps({'paramfile': astrastring.param, 'astra': astrastring.cmd_string, 'modelvars': modl}, indent=4)
		f.write(data2save)


	print('Data is saved to file: '+filename + '\n')
