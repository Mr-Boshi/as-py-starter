def suggester(modelvars, arraydata):
	from lib.as_processing import get_dyn_indices
	from lib.classes import errors

	time = arraydata[:, 0]
	prc  = arraydata[:, 5]
	pre  = arraydata[:, 11]

	prc_central = arraydata[:, 10]

	#Getting indecies to cut out dynamics and plots
	dynamics_indices = get_dyn_indices(time, modelvars.dyn_start, modelvars.dyndur)
	ascertion_ends   = None
	
	for i in range(dynamics_indices[0],0,-1):
		ascertion_0  = errors(prc[i], prc[i-1])
		ascertion_10 = errors(prc_central[i], prc_central[i-1])
		if ascertion_0.rel_error > 0.0 and ascertion_10.rel_error > 0.0:
			ascertion_ends=time[i]
			print('Suggested dynamic start time: {0}\n'.format(ascertion_ends))
			break
	
	
	print('Dynamics borders: {0} ... {1}\n'.format(time[dynamics_indices[0]], time[dynamics_indices[1]]))
	print(pre[dynamics_indices[0]], prc[dynamics_indices[0]])
	print(pre[dynamics_indices[1]], prc[dynamics_indices[1]])


	# Calculating perfect CNEUT1
	suggflag    = True
	sugg        = [float(modelvars.init_cneut), float(modelvars.end_cneut)]
	relation_init    = pre[dynamics_indices[0]] / prc[dynamics_indices[0]]
	relation_end    = pre[dynamics_indices[1]] / prc[dynamics_indices[1]]


	if relation_init > modelvars.sigma_error:
		new_cneut = round(sugg[0]*relation_init, 4)
		if new_cneut != sugg[0]:
			sugg[0] = new_cneut
			suggflag = False
		print('---')
		print('Suggested initial CNEUT: {0}\n'.format(sugg[0]))
	if relation_end > modelvars.sigma_error:
		new_cneut = round(sugg[1]*relation_end, 4)
		if new_cneut != sugg[1]:
			sugg[1] = new_cneut
			suggflag = False

		print('\nSuggested final CNEUT: {0}\n'.format(sugg[1]))
		print('---')

	return [suggflag, sugg]
