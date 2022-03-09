# Function to process astra results
def get_dyn_indices(time, dyn_start, dyn_duration):
	timedif1 = abs(time-float(dyn_start))
	timedif2 = abs(time-float(dyn_start)-dyn_duration)
	return [timedif1.argsort()[0], timedif2.argsort()[0]]

#-------------------------------------------------------------------------------
""" The main function ======================================================="""
#-------------------------------------------------------------------------------
def as_processing(np, arraydata, radarray, modelvars, columns):
	from lib.classes import diffusion_coefficients, tungsten_data, metrics
	np.seterr(divide='ignore', invalid='ignore')
	
	# Getting how many columns are in the data
	_,y = radarray.shape
	
	# Preallocating the dictionary with the colums that I watn to process
	my_columns = {'Rad': np.empty(y), 'n_Wc': np.empty(y), 'n_Wx': np.empty(y),
               'Prc': np.empty(y), 'Prx': np.empty(y), 'Van': np.empty(y), 
			   'Dan': np.empty(y), 'Vnc': np.empty(y), 'Dnc': np.empty(y)}

	# Putting radarray data into my dictionary
	for column in my_columns.keys():
		if column in columns:
			my_index = columns.index(column)
			my_columns[column] = radarray[:, my_index]

	# Creating vars
	# Time array and Time evolutions of Prad
	time = arraydata[:, 0]
	prc  = arraydata[:, 5:11]													# Calculation results
	pre  = arraydata[:, 11:17]													# Experimental data

	# Fixing subroutine flaws
	for i in range(1, len(pre)):
		if pre[i, 0] == 0:
			pre[i, :] = pre[i-1, :]

	# Setting radius, in sm
	r = 100*my_columns['Rad']

	# Transport coeffs
	nclass_coeffs = diffusion_coefficients(my_columns['Dnc'], my_columns['Vnc'])
	anomal_coeffs = diffusion_coefficients(my_columns['Dan'], my_columns['Van'])

	# Tungsten data
	tungsten_exp   = tungsten_data(my_columns['Prx'], pre, my_columns['n_Wx'])
	tungsten_model = tungsten_data(my_columns['Prc'], prc, my_columns['n_Wc'])

	#Getting indecies to cut out dynamics and plots
	dynind = get_dyn_indices(time, modelvars.dyn_start, modelvars.dyndur)

	# Calculating quality metric
	## Cutting the dynamic part of the calculation
	prc_removal = prc[dynind[0]:dynind[1]]
	pre_removal = pre[dynind[0]:dynind[1]]

	## Calculating relative difference between exp and calc data
	difference_removal  = prc_removal - pre_removal
	relative_difference = abs(difference_removal / pre_removal)


	## Preallocating metrics vars
	error_max    = []
	error_min    = []
	error_mean   = []
	model_metric = metrics()

	# Finding max/min/mean difference for each radial point
	_, array_points = relative_difference.shape
	for i in range(0,array_points):
		error_max.append(max(relative_difference[:,i]))
		error_min.append(min(relative_difference[:,i]))
		error_mean.append(np.mean(relative_difference[:, i]))

	# Setting them into metrics() obj.
	model_metric.set(error_max, error_min, error_mean)

	return [time, r,						\
			tungsten_exp, tungsten_model,	\
			anomal_coeffs, nclass_coeffs,	\
         	model_metric, dynind]
