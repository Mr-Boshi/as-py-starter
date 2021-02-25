def modelsetting(model_name, modelvars, anomvars, dyndur, sys):						# Setting up the model
	file = open('equ/'+model_name).read().splitlines()

	# calculation settings
	file[1] = 'CV4='+modelvars.init_cneut+';						! Initial CNEUT1'
	file[2] = 'CV5='+modelvars.end_cneut+';						! Final   CNEUT1'
	file[3] = 'CV6='+modelvars.dyn_start+';						! Start Dynamics'
	file[4] = 'CV7='+str(dyndur)+';						! Duration of detaled calculation'

	# Anomalous coefficients
	if len(anomvars) < 12:
		print('Unsufficient data to set anomalous transport. Should be 12 variables')
		sys.exit()
	else:
		file[8]  = 'CF5='+ anomvars[0]+';'
		file[9]  = 'CF6='+ anomvars[1]+';'
		file[10] = 'CF7='+ anomvars[2]+';'
		file[11] = 'CF8='+ anomvars[3]+';'
		file[12] = 'CF9='+ anomvars[4]+';'
		file[13] = 'CF10='+anomvars[5]+';'
		file[14] = 'CF11='+anomvars[6]+';'
		file[15] = 'CF12='+anomvars[7]+';'
		file[16] = 'CF13='+anomvars[8]+';'
		file[17] = 'CF14='+anomvars[9]+';'
		file[18] = 'CF15='+anomvars[10]+';'
		file[19] = 'CF16='+anomvars[11]+';'

	open('equ/'+model_name, 'w').write('\n'.join(file))
