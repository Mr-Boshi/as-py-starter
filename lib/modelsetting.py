def modelsetting(model_name, modelvars, anomvars, dyndur, sys):						# Setting up the model
	with open('equ/'+model_name, 'r') as f:
		file = f.readlines()

	# calculation settings
	file[1] = 'CV4='+modelvars.init_cneut+';					! Initial CNEUT1' 					+ '\n'
	file[2] = 'CV5='+modelvars.end_cneut+';						! Final   CNEUT1' 					+ '\n'
	file[3] = 'CV6='+modelvars.dyn_start+';						! Start Dynamics' 					+ '\n'
	file[4] = 'CV7='+str(dyndur)+';								! Duration of detaled calculation'	+ '\n'

	# Anomalous coefficients
	if len(anomvars) < 12:
		print('Unsufficient data to set anomalous transport. Should be 12 variables')
		sys.exit()
	else:
		for i in range(12):
			file[8+i]  = 'CF' + str(5+i) + ' = ' + anomvars[i]+';' + '\n'

	# Other settings

	file[21] = '! TINIT	= 0.0;							! Start of recording (does not matter)'	+ '\n'
	file[22] = '! TSCALE= 999;							! Recorded time interval'				+ '\n'
	file[25] = 'DTOUT	= CIMP4'																+ '\n'
	file[23] = 'CNEUT1	= CV4+(CV5-CV4)*FJUMP(CV6+CIMP4)'										+ '\n'
	file[24] = 'CIMP4	= 0.01-0.009*FJUMP(CV6-0.01)+0.009*FJUMP(CV6+CV7+0.01)'					+ '\n'
	file[27] = 'CV8		= 2*CV6+CV7+2*CIMP4				! End time'								+ '\n'				
	file[28] = 'tostop:999:CV8:							! Closing astra'						+ '\n'

	with open('equ/'+model_name, 'w') as f:
		f.writelines(file)
