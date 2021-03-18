def modelsetting(model_name, exp_file, modelvars, dyndur, transp_sett):						# Setting up the model
	from lib.dynreader import line_finder

	with open('equ/'+model_name, 'r') as f:
		file = f.readlines()

	rad_coeff_line = []
	rad_search_keys = ['PRC0', 'PRC1', 'PRC2', 'PRC3', 'PRC4', 'PRC5',
                    'PRE0', 'PRE1', 'PRE2', 'PRE3', 'PRE4', 'PRE5', 
					'CV4=', 'CV5=', 'CV6=', 'CV7=',
                    'CNEUT1=', 'CIMP4 =', 'DTOUT =', 'CV8=']
	for word in rad_search_keys:
		rad_coeff_line.append(line_finder(file, word)[0] - 1)
	prc_lines = rad_coeff_line[0:6]
	pre_lines = rad_coeff_line[6:12]
	cv_lines  = rad_coeff_line[12:16]
	par_lines = rad_coeff_line[16:20]

	# Calculation settings
	file[cv_lines[0]] = 'CV4='+modelvars.init_cneut+';						! Initial CNEUT1' 					+ '\n'
	file[cv_lines[1]] = 'CV5='+modelvars.end_cneut+';						! Final   CNEUT1' 					+ '\n'
	file[cv_lines[2]] = 'CV6='+modelvars.dyn_start+';						! Start Dynamics' 					+ '\n'
	file[cv_lines[3]] = 'CV7='+str(dyndur)+';								! Duration of detaled calculation'	+ '\n'

	# Other settings
	file[par_lines[0]] = 'CNEUT1= CV4+(CV5-CV4)*FJUMP(CV6+CIMP4)'										+ '\n'
	file[par_lines[1]] = 'CIMP4=  0.01-0.009*FJUMP(CV6-0.01)+0.009*FJUMP(CV6+CV7+0.01)'					+ '\n'
	file[par_lines[2]] = 'DTOUT=  CIMP4'																+ '\n'
	file[par_lines[3]] = 'CV8=    2*CV6+CV7+2*CIMP4				! End time'								+ '\n'	

	counter = 0
	for line in prc_lines:
		file[line] = 'PRC{0}_CAR3({1});\n'.format(
			counter, transp_sett.output_radii[counter])
		counter += 1

	counter = 0
	for line in pre_lines:
		file[line] = 'PRE{0}_{1}X({2});\n'.format(
			counter, modelvars.dynam_name, transp_sett.output_radii[counter])
		counter += 1
	

	with open('equ/'+model_name, 'w') as f:
		f.writelines(file)




	# Anomalous coefficients
	with open('exp/'+exp_file, 'r') as f:
		file = f.readlines()

	search_keys = ['CAR9', 'CAR10']
	coeff_line=[]
	for word in search_keys:
		coeff_line.append(line_finder(file, word)[0])

	dn_lines  = [coeff_line[0]+2, coeff_line[0]+3]
	cn_lines  = [coeff_line[1]+2, coeff_line[1]+3]

	points = len(transp_sett.radii.split())
	if not points == len(transp_sett.an_dif.split()) == len(transp_sett.an_pinch.split()):
		print('Anomalous transport oefficients ar not matching sizes. Exiting the program')
		exit()

	file[dn_lines[0]-3] = 'GRIDTYPE  18  POINTS {} NAMEXP  CAR9   NTIMES 1'.format(points) + '\n'
	file[cn_lines[0]-3] = 'GRIDTYPE  18  POINTS {} NAMEXP  CAR10   NTIMES 1'.format(points) + '\n'

	file[dn_lines[0]] = transp_sett.radii + '\n'
	file[cn_lines[0]] = transp_sett.radii + '\n'

	file[dn_lines[1]] = transp_sett.an_dif +   '\n'
	file[cn_lines[1]] = transp_sett.an_pinch + '\n'

	with open('exp/' + exp_file, 'w') as f:
		f.writelines(file)



