'''
	Function to suggest CNEUT
'''

def suggester(modelvars, arraydata, dyndur):
	from lib.as_processing import get_dyn_indices
	from lib.classes import errors

	time = arraydata[:, 0]
	prc  = arraydata[:, 5]
	pre  = arraydata[:, 11]

	prc_central = arraydata[:, 10]
	pre_central = arraydata[:, 16]

	#Getting indecies to cut out dynamics and plots
	dynamics_indices = get_dyn_indices(time, modelvars.dyn_start, dyndur)
	ascertion_ends   = None
	
	for i in range(dynamics_indices[0],0,-1):
		ascertion_0  = errors(prc[i], prc[i-1])
		ascertion_10 = errors(prc_central[i], prc_central[i-1])
		if ascertion_0.rel_error > 0.0 and ascertion_10.rel_error > 0.0:
			ascertion_ends=time[i]
			print('Suggested dynamic start time: {0}\n'.format(ascertion_ends))
			break
	
	
	# print('Dynamics borders: {0} ... {1}\n'.format(time[dynamics_indices[0]], time[dynamics_indices[1]]))
	
	# Calculating perfect CNEUT1
	suggflag    = True
	sugg        = [float(modelvars.init_cneut), float(modelvars.end_cneut)]
	init_errors = errors(pre[dynamics_indices[0]], prc[dynamics_indices[0]])
	end_errors  = errors(pre[dynamics_indices[1]], prc[dynamics_indices[1]])

	if init_errors.rel_error > modelvars.sigma_error:
		sugg[0] = round(sugg[0]*init_errors.error, 4)
		suggflag = False
		print('---')
		print('Suggested initial CNEUT: {0}\n'.format(sugg[0]))
	if end_errors.rel_error > modelvars.sigma_error:
		sugg[1] = round(sugg[1]*end_errors.error, 4)
		suggflag = False
		print('\nSuggested final CNEUT: {0}\n'.format(sugg[1]))
		print('---')

	return [suggflag, sugg]
