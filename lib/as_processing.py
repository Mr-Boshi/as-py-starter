# Function to process astra results
def as_processing(arraydata, radarray, dyndur, modelvars):
	import numpy as np
	np.seterr(divide='ignore', invalid='ignore')
	
	#Creating vars
	# Time and radius (in cm)
	time = arraydata[:, 0]
	r    = 100*radarray[:, 0]

	# Time evolution of Prad
	prc = arraydata[:, 5:11]
	pre = arraydata[:, 11:17]

	# Radial profiles of Prad
	pwcalc = radarray[:, 1]
	pwexp = radarray[:, 2]

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
	timedif1 = abs(time-float(modelvars.dyn_start))
	timedif2 = abs(time-float(modelvars.dyn_start)-dyndur)
	dynind   = [timedif1.argsort()[0], timedif2.argsort()[0]]

	# Fixing subroutine flaws
	for i in range(1, len(pre)):
		if pre[i, 0] == 0:
			pre[i, :] = pre[i-1, :]

	# Mean square error
	pr_err = 100*(np.sum((prc[dynind[0]:dynind[1]]-pre[dynind[0]:dynind[1]])**2, 0)/len(prc[dynind[0]:dynind[1], 0]))**0.5

	# Debug printing

	# print('time')
	# print(time)
	# print('r')
	# print(r)
	# print('prc')
	# print(prc)
	# print('pre')
	# print(pre)
	# print('pwcalc')
	# print(pwcalc)
	# print('pwexp')
	# print(pwexp)
	# print('van')
	# print(van)
	# print('dan')
	# print(dan)
	# print('vneo')
	# print(vneo)
	# print('dneo')
	# print(dneo)
	# print('nWtot')
	# print(nWtot)
	# print('gradnW')
	# print(gradnW)
	# print('grWvnW')
	# print(grWvnW)
	# print('timedif1')
	# print(timedif1)
	# print('timedif2')
	# print(timedif2)
	# print('dynind')
	# print(dynind)


	return [time, r, prc, pre, pwcalc, pwexp, van, dan, vneo, dneo, nWtot, gradnW, grWvnW, pr_err, dynind]

