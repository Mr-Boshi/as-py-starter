def datfilesaver(file_descriptor, time, r, prc, pre, pwcalc, pwexp, van, dan, vneo, dneo, nWtot, gradnW, grWvnW, pr_err, tm, astrastring, modelvars, anomvars):
	from scipy.io import savemat
	import numpy as np
	import json


	localtime = tm.localtime(tm.time())
	timndat = str(localtime.tm_year)+'.'+str(localtime.tm_mon)+'.'+str(localtime.tm_mday) + \
	  '-'+str(localtime.tm_hour)+'.' + \
	  str(localtime.tm_min)+'.'+str(localtime.tm_sec)
	filename = timndat+' '+astrastring.exp+' '+astrastring.model

	filename = 'dat/pydat/'+filename

	# Constructing sh command string
	startastra = '.exe/astra '+' '+astrastring.exp\
	  + ' '+astrastring.model\
	  + ' '+astrastring.st_time\
	  + ' '+astrastring.end_time\
	  + ' '+astrastring.back_key
	anom = [float(i) for i in anomvars]
	modl = [float(modelvars.init_cneut), float(modelvars.end_cneut), float(modelvars.dyn_start), float(modelvars.cycle_key)]

	if file_descriptor == 'mat':
		filename = filename+'.mat'
		mdict = {'r': r, 'time': time, 'prc': prc, 'pre': pre, 'pwcalc': pwcalc, 'pwexp': pwexp, 'van': van, 'dan': dan, 'vneo': vneo, 'dneo': dneo,
		  'nWtot': nWtot, 'gradnW': gradnW, 'grWvnW': grWvnW, 'paramfile': astrastring['param'], 'astra': startastra, 'modelvars': modl, 'anomvars': anom}
		savemat(filename, mdict)

	else:
		filename = filename+'.' + file_descriptor
		with open(filename, 'w') as f:
			time_points=time.size
			radial_points=r.size


		# Radius (in cm)
			np.savetxt(f, r.reshape((-1, radial_points)), fmt="%10.5f",
			           header='Radius (in cm):', footer='#')
		# Radial profiles of Prad
			np.savetxt(f, pwcalc.reshape((-1, radial_points)), fmt="%10.5f",
			           header='Calculated radial profile of Prad:', footer='#')
			np.savetxt(f, pwexp.reshape((-1, radial_points)), fmt="%10.5f",
			           header='Experimental radial profile of Prad:', footer='#')
		# Anomalous coefficients
			np.savetxt(f, dan.reshape((-1, radial_points)),
			           fmt="%10.5f", header='Anomalous diffusion:', footer='#')
			np.savetxt(f, van.reshape((-1, radial_points)),
			           fmt="%10.5f", header='Anomalous pinch:', footer='#')
		# Neoclassic coefficients
			np.savetxt(f, dneo.reshape((-1, radial_points)),
			           fmt="%10.5f", header='Neoclassic diffusion:', footer='#')
			np.savetxt(f, vneo.reshape((-1, radial_points)),
			           fmt="%10.5f", header='Neoclassic pinch:', footer='#')
		# W density profile
			np.savetxt(f, nWtot.reshape((-1,radial_points)),
			           fmt="%10.5f", header='Total impurity density:', footer='#')

			np.savetxt(f, gradnW.reshape((-1,radial_points)), fmt="%10.5f", header='gradnW:', footer='#')
			np.savetxt(f, grWvnW.reshape((-1,radial_points)), fmt="%10.5f", header='grW/vnW:', footer='#')

			f.write('\n')

		# Times
			np.savetxt(f, time.reshape((1,time_points)), fmt="%10.5f", header='Times:', footer='#')
		# Time evolution of Prad
			prc_shaped = prc.reshape((time_points, -1))
			np.savetxt(f, prc_shaped.transpose(), fmt="%10.5f",
			           header='Calculated time evolution of Prad:', footer='#')
			pre_shaped = pre.reshape((time_points, -1))
			np.savetxt(f, pre_shaped.transpose(), fmt="%10.5f",
			           header='Experimental time evolution of Prad:', footer='#')

			f.write('\n')

			f.write('# Calculation settings')			
			data2save = json.dumps({'paramfile': astrastring.param, 'astra': startastra, 'modelvars': modl, 'anomvars': anom})
			f.write(data2save)


	print('Data is be saved into file: '+filename + '\n')
