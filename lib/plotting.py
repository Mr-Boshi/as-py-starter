# Function to plot time evolution
def timeplotter(pt, subplot_settings, time, indices, model_dynamics, experimental_dynamics, plot_rad):
	pt.subplot(subplot_settings[0], subplot_settings[1], subplot_settings[2])

	pt.plot(time[indices[0]:indices[1]],
	        model_dynamics[indices[0]:indices[1]], label='Calculation')
	pt.plot(time[indices[0]:indices[1]],
	        experimental_dynamics[indices[0]:indices[1]], label='Experiment')

	pt.xlabel('time')
	pt.ylabel('P_rad('+str(plot_rad)+')')
	pt.legend()
	pt.grid()


def plotting(pt, radii, r, time, dynamics_indices, tungsten_model, tungsten_exp, anomal_coeffs, nclass_coeffs, grWvnW):
	fig = pt.figure()  # an empty figure with no axes
	fig.suptitle('W removal')  # Add a title so we know which it is
	for i in range(0, 6):
			timeplotter(pt, [2, 3, i+1], time, dynamics_indices,
			            tungsten_model.density_dynamics[:, i], tungsten_exp.density_dynamics[:, i], radii[i])

	#-------------------------------------------------------------------------------

	# fig1 = pt.figure()
	# pt.subplot(1,2,1)
	# pt.plot([0, 3, 6, 9, 12, 15], pr_err)
	# pt.xlabel('r, cm')
	# pt.ylabel('S_0, %')
	# pt.grid()

	#-------------------------------------------------------------------------------

	fig2 = pt.figure()
	pt.subplot(2, 3, 3)
	pt.plot(r, tungsten_model.radiation_losses, 'b-', label='Calculation')
	pt.plot(r, tungsten_exp.radiation_losses, 'g-', label='Experiment')
	pt.xlabel('r, cm')
	pt.ylabel('P_rad')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 2)
	pt.plot(r, anomal_coeffs.pinch, 'b-', label='Anomalous')
	pt.plot(r, nclass_coeffs.pinch, 'g-', label='Neoclassic')
	pt.xlabel('r, cm')
	pt.ylabel('V')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 1)
	pt.plot(r, anomal_coeffs.diffusion, 'b-', label='Anomalous')
	pt.plot(r, nclass_coeffs.diffusion, 'g-', label='Neoclassic')
	pt.xlabel('r, cm')
	pt.ylabel('D')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 4)
	pt.plot(r, tungsten_model.total_density)
	pt.xlabel('r, cm')
	pt.ylabel('nW')
	pt.grid()

	pt.subplot(2, 3, 5)
	vvdneo = nclass_coeffs.pinch/nclass_coeffs.diffusion
	vvdneo[0] = 0

	#---------------------------------------------------------------------------
	pt.plot(r, vvdneo, label='vneo/dneo')
	pt.plot(r, grWvnW, label='gradNW/NW')
	pt.xlabel('r, cm')
	pt.ylabel('peaking factors')
	pt.legend()
	pt.grid()

	pt.subplot(2, 3, 6)
	pt.plot(r, tungsten_exp.radiation_losses/tungsten_model.radiation_losses)
	pt.plot([0, 30], [1, 1], 'k--')
	pt.ylabel('Prad_exp/Prad_calc')
	pt.grid()

	pt.show()
