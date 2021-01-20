def matfilesaver(time, r, prc, pre, pwcalc, pwexp, van, dan, vneo, dneo, nWtot, gradnW, grWvnW, pr_err, tm, astrastring, anomvars, modelvars):
	from scipy import savemat
	localtime = tm.localtime(tm.time())
	timndat = str(localtime.tm_year)+'.'+str(localtime.tm_mon)+'.'+str(localtime.tm_mday) + \
            '-'+str(localtime.tm_hour)+':' + \
            str(localtime.tm_min)+':'+str(localtime.tm_sec)
	filename = timndat+' '+astrastring['exp']+' '+astrastring['model']+'.mat'
	print('Data will be saved into file: '+filename)
	filename = 'dat/pydat/'+filename

	# Constructing sh command string
	startastra = '.exe/astra '+' '+astrastring['exp']\
            + ' '+astrastring['model']\
            + ' '+astrastring['st_time']\
            + ' '+astrastring['end_time']\
            + ' '+astrastring['backkey']
	anom = [float(i) for i in anomvars]
	modl = [float(i) for i in modelvars]
	mdict = {'r': r, 'time': time, 'prc': prc, 'pre': pre, 'pwcalc': pwcalc, 'pwexp': pwexp, 'van': van, 'dan': dan, 'vneo': vneo, 'dneo': dneo,
          'nWtot': nWtot, 'gradnW': gradnW, 'grWvnW': grWvnW, 'paramfile': astrastring['param'], 'astra': startastra, 'modelvars': modl, 'anomvars': anom}
	savemat(filename, mdict)
