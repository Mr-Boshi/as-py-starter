def suggester(modelvars, arraydata, dyndur):													# Function to suggest CNEUT
	time = arraydata[:, 0]
	prc  = arraydata[:, 5]
	pre  = arraydata[:, 11]

	#Getting indecies to cut out dynamics and plots
	timedif1 = abs(time-float(modelvars.dyn_start))
	timedif2 = abs(time-float(modelvars.dyn_start)-dyndur)
	times = [timedif1.argsort()[0]-1, timedif2.argsort()[0]+1]

	print('Dynamics borders: '+str(time[times[0]])+', '+str(time[times[1]]))

	# Calculating perfect CNEUT1
	err_init = pre[times[0]]/prc[times[0]]
	err_end  = pre[times[1]]/prc[times[1]]
	errs     = [err_init, err_end]

	suggflag = 1
	sugg = [float(modelvars.init_cneut), float(modelvars.end_cneut)]

	dop_err = 0.02
	if abs(errs[0]-1) > dop_err:
		print('---')
		print('Suggested initial CNEUT: ', str(float(modelvars.init_cneut)*errs[0]))
		sugg[0] = sugg[0]*errs[0]
		suggflag = 0
	if abs(errs[1]-1) > 0.002:
		print('\nSuggested final CNEUT: ', str(float(modelvars.end_cneut)*errs[1]))
		print('---')
		sugg[1] = sugg[1]*errs[1]
		suggflag = 0
	return [suggflag, sugg]
