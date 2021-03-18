# Function to process astra results
def get_dyn_indices(time, dyn_start, dyn_duration):
	timedif1 = abs(time-float(dyn_start))
	timedif2 = abs(time-float(dyn_start)-dyn_duration)
	return [timedif1.argsort()[0], timedif2.argsort()[0]]

def as_processing(np, arraydata, radarray, dyndur, modelvars):
	from lib.classes import diffusion_coefficients, tungsten_data, metrics
	np.seterr(divide='ignore', invalid='ignore')
	
	#Creating vars
	# Time and radius (in cm)
	time = arraydata[:, 0]
	r    = 100*radarray[:, 0]

	# Time evolution of Prad
	prc = arraydata[:,  5:11]
	pre = arraydata[:, 11:17]

	# Radial profiles of Prad
	pwcalc = radarray[:, 1]
	pwexp  = radarray[:, 2]

	# Anomalous coefficients
	van = radarray[:, 3]
	dan = radarray[:, 4]

	# Neoclassic coefficients
	vneo = radarray[:, 5]
	dneo = radarray[:, 6]

	# W density profile
	nWtot = radarray[:, 7]

	gradnW = np.gradient(nWtot)
	grWvnW = gradnW/nWtot

	#Getting indecies to cut out dynamics and plots
	dynind = get_dyn_indices(time, modelvars.dyn_start, dyndur)

	# Fixing subroutine flaws
	for i in range(1, len(pre)):
		if pre[i, 0] == 0:
			pre[i, :] = pre[i-1, :]

	# Quality metric
	prc_removal = prc[dynind[0]:dynind[1]]
	pre_removal = pre[dynind[0]:dynind[1]]

	difference_removal = prc_removal - pre_removal
	relative_difference = abs(difference_removal / pre_removal)

	# model_metrics = metrics()

	array_length, array_points = relative_difference.shape

	error_max=[]
	error_min=[]
	error_mean = []
	for i in range(0,array_points):
		error_max.append(max(relative_difference[:,i]))
		error_min.append(min(relative_difference[:,i]))
		error_mean.append(np.mean(relative_difference[:, i]))

	model_metric = metrics()
	model_metric.min = error_min
	model_metric.max = error_max
	model_metric.mean = error_mean


	# pr_err = 100*(np.sum(((prc[dynind[0]:dynind[1]]-pre[dynind[0]:dynind[1]])/pre[dynind[0]:dynind[1]])**2, 0)/len(prc[dynind[0]:dynind[1], 0])))**0.5
	pr_err = 0

	nclass_coeffs = diffusion_coefficients(dneo, vneo)
	anomal_coeffs = diffusion_coefficients(dan, van)

	tungsten_exp   = tungsten_data(pwexp, pre)
	tungsten_model = tungsten_data(pwcalc, prc, nWtot)


	return [time, r,						\
			tungsten_exp, tungsten_model,	\
			anomal_coeffs, nclass_coeffs,	\
         gradnW, grWvnW, model_metric, dynind]
